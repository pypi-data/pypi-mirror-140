# Calliope
# Copyright (C) 2021  Kilian Lackhove <kilian@lackhove.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Select Musicbrainz matches for playlist items by weighted priorities"""

import logging
from bisect import bisect_left
from collections import defaultdict
from difflib import SequenceMatcher
from math import log10
from typing import Iterable, Iterator, List, Optional
from unicodedata import normalize

from calliope.playlist import Item
from calliope.utils import FeatMode, get_isrcs, normalize_creator_title

log = logging.getLogger(__name__)


def select_best(item: Item, candidates: List[Item]) -> Optional[Item]:
    """
    Automatically select the best match Item from a list of candidates for a given item.

    For each candidate, a number of weighted priorities is computed, which
    comprise its overall priority. The item with the best priority is automatically
    selected if it is higher than 90%.

    Args:
        item: A calliope playlist item to match
        candidates: A list of candidates

    Returns:
        The best match Item or None if no good match was found.

    """

    candidates = sorted(
        _annotate_priority(item, candidates),
        key=lambda x: x["_.priority"],
        reverse=True,
    )
    candidates = list(_filter_duplicate_recordings(candidates))

    if len(candidates) > 0 and candidates[0]["_.priority"] >= 0.90:
        log.info(
            "selected {0} ({1:5.2f}%) for {2}".format(
                _format_candidate(candidates[0]),
                candidates[0]["_.priority"] * 100,
                _format_candidate(item),
            )
        )
        return candidates[0]
    else:
        log.warning("No match found for {}:".format(_format_candidate(item)))
        for cand in candidates[:10]:
            log.info(
                "{0:5.2f}%: {1}".format(
                    cand["_.priority"] * 100, _format_candidate(cand)
                )
            )
        return None


def select_interactive(item: Item, candidates: List[Item]) -> Optional[Item]:
    """
    Select the best match Item from a list of candidates for a given item,
    with asking the user for help if in doubt.

    For each candidate, a number of weighted priorities is computed, which
    comprise its overall priority. The item with the best priority is automatically
    selected if it is higher than 95%, otherwise the user is asked for help.

    Args:
        item: A calliope playlist item to match
        candidates: A list of candidates

    Returns:
        The best match Item or None if no good match was found.

    """
    candidates = sorted(
        _annotate_priority(item, candidates),
        key=lambda x: x["_.priority"],
        reverse=True,
    )
    candidates = list(_filter_duplicate_recordings(candidates))

    if candidates[0]["_.priority"] >= 0.95:
        match = candidates[0]
        log.info(
            "selected {0} ({1:5.2f}%) for {2} from {3} candidates".format(
                _format_candidate(candidates[0]),
                candidates[0]["_.priority"] * 100,
                _format_candidate(item),
                len(candidates)
            )
        )
    else:
        print(f"\nBest {len(candidates)} candidates for {_format_candidate(item)}:")
        selection = None
        offset = 0
        while selection is None:
            for i, candidate in enumerate(
                candidates[offset : offset + 20], start=offset
            ):
                print(
                    f'{i + 1:2d} ({candidate["_.priority"] * 100:5.2f}%): {_format_candidate(candidate)}'
                )
            while True:
                answer = input(
                    "Select a match (Press Enter to skip, n for next 20 results): "
                )
                if answer == "":
                    return None
                if answer == "n":
                    break

                try:
                    i = int(answer) - 1
                except ValueError:
                    continue

                if 0 <= i < offset + 20:
                    selection = i
                    break

            offset += 20

        match = candidates[selection]

    return match


def _format_candidate(candidate: Item) -> str:
    """
    Create a human readable presentation of a candidate Item.

    Args:
        candidate: A calliope playlist Item.

    Returns:
        The string representation of the item.
    """

    main_fields = []

    if "creator" in candidate:
        main_fields.append(candidate["creator"])

    if "album" in candidate:
        album_fields = []

        album_fields.append(candidate.get("_.albumartist", candidate.get("creator")))
        album_fields.append(candidate.get("_.date"))
        if "_.medium-track-count" in candidate:
            album_fields.append(f'{candidate["_.medium-track-count"]} tracks')
        album_fields.append(candidate.get("_.status"))
        main_fields.append(
            candidate["album"]
            + " ("
            + ", ".join(f for f in album_fields if f is not None)
            + ")"
        )

    if "title" in candidate:
        main_fields.append(candidate["title"])

    return " - ".join(main_fields)


def _filter_duplicate_recordings(sorted_candidates: Iterable[Item]) -> Iterator[Item]:
    """
    Remove duplicate candidate Items.

    Duplicates are identified by their creator, album, title and number of tracks
    of their album. The first occurrence of is kept, so this function is most
    useful if the candidates are sorted by priority in descending order.

    Args:
        sorted_candidates: An iterable of candidate Items, preferably sorted by
            their priority in descending order

    Returns:
        An iterable of candidate items

    """
    seen = set()
    for candidate in sorted_candidates:
        if "title" not in candidate:
            yield candidate
            continue

        key = (
            candidate.get("creator", ""),
            candidate.get("album", ""),
            candidate.get("title", ""),
            candidate.get("_.medium-track-count", ""),
        )
        if key in seen:
            continue

        yield candidate
        seen.add(key)


def _annotate_priority(item: Item, candidates: Iterable[Item]) -> Iterator[Item]:
    """
    Annotate each candidate with its priority.

    The weights and priorities are stored as two element tuples in the
    _.weighted_priorities dict. Weights can be any positive number, where 100
    marks the reference as this value is used for the similarities of title,
    album and creator. Scores can be any number between 0 and 1. The candidates
    overall priority is computed from its weighted priorities and stored in
    "_.priority".

    Args:
        item: A playlist item that is to be matched
        candidates: An iterable of match candidates.

    Returns:
        The annotated but unsorted candidates

    """
    candidates = _annotate_static_recording_priorities(candidates)
    candidates = _annotate_static_release_priorities(candidates)
    candidates = _annotate_release_date_priority(candidates)
    candidates = (_annotate_similarity(item, c) for c in candidates)
    candidates = (_annotate_musicbrainz(item, c) for c in candidates)
    candidates = (_annotate_spotify(item, c) for c in candidates)

    for candidate in candidates:
        priorities = candidate["_.weighted_priorities"]
        priority = sum(w * p for w, p in priorities.values()) / sum(
            w for w, p in priorities.values()
        )
        candidate["_.priority"] = priority

        yield candidate


def _annotate_static_recording_priorities(candidates: Iterable[Item]) -> Iterator[Item]:
    """
    Annotate candidates with priorities which are independent of the reference
        item and based on their recording, if present.

    Priorities:
        - recording.isrcs: A penalty for items without ISRC with a tiny weight.
        - recording.mb_score: A priority based on the score returned by the
                musicbrainz search API
        - recording.release_count: A priority to favor recordings with many releases
    """
    for candidate in candidates:
        if "title" not in candidate:
            yield candidate
            continue

        weighted_priorities = candidate.setdefault("_.weighted_priorities", dict())

        if len(get_isrcs(candidate)) <= 0:
            weighted_priorities["recording.isrcs"] = (1, 0)

        if "_.mb_score" in candidate:
            weighted_priorities["recording.mb_score"] = (
                10,
                int(candidate["_.mb_score"]) / 100,
            )

        if "spotify.popularity" in candidate:
            weighted_priorities["recording.spotify_popularity"] = (
                10,
                int(candidate["spotify.popularity"]) / 100,
            )

        if "_.release_count" in candidate:
            weighted_priorities["recording.release_count"] = (
                5,
                min(1.0, candidate["_.release_count"] / 10),
            )

        yield candidate


def _annotate_static_release_priorities(candidates: Iterable[Item]) -> Iterator[Item]:
    """
    Annotate candidates with priorities which are independent of the reference item
    and based on their release, if present.

    Priorities:
        - release.secondary_types: A penalty for different release types with
                dynamic weight based on the least favorable type
        - release.status: A penalty for unofficial releases
        - release.sampler: A penalty for samplers, i.e. releases with
                "Various Artists" as albumartist
    """
    for candidate in candidates:
        if "album" not in candidate:
            yield candidate
            continue

        weighted_priorities = candidate.setdefault("_.weighted_priorities", dict())

        secondary_types = candidate.get("_.secondary-type-list", [])
        for st in secondary_types:
            weight = {
                "compilation": 5,
                "remix": 5,
                "soundtrack": 5,
                "dj-mix": 5,
                "demo": 20,
                "live": 15,
                "mixtape/street": 20,
                "interview": 100,
                "spokenword": 100,
                "audiobook": 100,
                "album": -1,
                "single": -1,
            }.get(st.casefold())
            if weight is None:
                log.warning("secondary type {} not recognized".format(st))
            if (
                weight is not None
                and weight
                > weighted_priorities.get("release.secondary_types", (0, 0))[0]
            ):
                weighted_priorities["release.secondary_types"] = (weight, 0)

        if candidate.get("_.status", "Official") != "Official":
            weighted_priorities["release.status"] = (20, 0)

        if candidate.get("_.albumartist", "").casefold() == "various artists":
            weighted_priorities["release.sampler"] = (5, 0)

        yield candidate


def _annotate_release_date_priority(candidates: Iterable[Item]) -> Iterator[Item]:
    """
    Add a weighted priority to each release of the same primary artist based on
    its distance to the artists first release.

    The priority is not computed from the temporal distance itself, but from the
    number of releases between the current and the first release.

    Priorities:
        - recording.release-date: A priority between 0 and 1 which favors the
            first release of its primary artist.
    """
    release_dates_by_artists = defaultdict(list)
    candidates = list(candidates)

    for candidate in candidates:
        sort_date = candidate.get("_.sort_date")
        if sort_date is not None:
            release_dates_by_artists[candidate.get("creator", "")].append(sort_date)

    for k, v in release_dates_by_artists.items():
        release_dates_by_artists[k] = sorted(set(v))

    for candidate in candidates:
        if "album" not in candidate:
            yield candidate
            continue

        weighted_priorities = candidate.setdefault("_.weighted_priorities", dict())

        sort_date = candidate.get("_.sort_date")
        if sort_date is None:
            weighted_priorities["recording.release-date"] = (10, 0.0)
        else:
            release_dates = release_dates_by_artists[candidate.get("creator", "")]
            if len(release_dates) > 1:
                ind = bisect_left(release_dates, sort_date)
                weighted_priorities["recording.release-date"] = (
                    1,
                    1 - ind / (len(release_dates) - 1),
                )
        yield candidate


def _annotate_similarity(item: Item, candidate: Item) -> Item:
    """
    Add weighted priorities based on the candidates similarity to the
    reference item.

    Priorities:
        - similarity.title: A priority based on the similarity of titles
        - similarity.creator: A priority based on the similarity of creators
        - similarity.album: A priority based on the similarity of album names
        - similarity.duration: A priority based on the candidates duration. Different
            units (e.g. milliseconds vs seconds) are scaled automatically.
        - similarity.isrc: A priority based on identical ISRCs. If these are
            identical, the candidate is considered a perfect match, hence the
            high priority. If there are more than one perfect matches, the
            remaining priorities are still relevant.

    """

    def compare_strings(a, b):
        return SequenceMatcher(
            None, normalize("NFKD", a).casefold(), normalize("NFKD", b).casefold()
        ).ratio()

    artist_i, title_i = normalize_creator_title(
        item.get("creator"), item.get("title"), feat_mode=FeatMode.DROP
    )
    artist_c, title_c = normalize_creator_title(
        candidate.get("creator"), candidate.get("title"), feat_mode=FeatMode.DROP
    )

    # TODO: evaluate alternative metrics, e.g. levensthein, jaro

    weighted_priorities = candidate.setdefault("_.weighted_priorities", dict())

    if title_i is not None and title_c is not None:
        title_ratio = compare_strings(title_i, title_c)
        weighted_priorities["similarity.title"] = (100, title_ratio)

    if artist_i is not None and artist_c is not None:
        artist_ratio = compare_strings(artist_i, artist_c)
        weighted_priorities["similarity.creator"] = (100, artist_ratio)

    album_i = item.get("album")
    album_c = candidate.get("album")
    if album_i is not None and album_c is not None:
        album_ratio = compare_strings(album_i, album_c)
        weighted_priorities["similarity.album"] = (100, album_ratio)

    duration_i = item.get("duration")
    duration_c = candidate.get("duration")
    if duration_i is not None and duration_c is not None:
        # in case mb_duration and duration are more than three decades apart,
        # scale them to the next SI unit prefix
        f_pow = round(log10(duration_c / duration_i))
        if f_pow % 3 == 0:
            duration_i = duration_i * 10 ** f_pow

        duration_ratio = 1.0 - (
            abs(duration_i - duration_c) / max(duration_i, duration_c)
        )
        weighted_priorities["similarity.duration"] = (50, duration_ratio)

    isrcs_i = get_isrcs(item)
    isrcs_c = get_isrcs(candidate)
    if len(set(isrcs_i) & set(isrcs_c)) > 0:
        weighted_priorities["similarity.isrc"] = (1e6, 1.0)

    return candidate


def _annotate_musicbrainz(item: Item, candidate: Item) -> Item:
    """
    Annotate priorities based on musicbrainz IDs.

    Depending on whether candidate is a track, an album or an artist, the main
    weight is set to 1E6, similar to  similarity.isrc in _annotate_similarity
    and all remaining weights are two decades smaller since they dont indicate
    perfect matches but imply that all other candidates should be neglected.
    """

    weighted_priorities = candidate.setdefault("_.weighted_priorities", dict())

    if item.get("musicbrainz.recording_id", "a") == candidate.get(
        "musicbrainz.recording_id", "b"
    ):
        weighted_priorities["musicbrainz.recording_id"] = (1e6, 1)

    if item.get("musicbrainz.release_group_id", "a") == candidate.get(
        "musicbrainz.release_group_id", "b"
    ):
        if "title" in candidate:
            weighted_priorities["musicbrainz.release_group_id"] = (1e4, 1)
        else:
            weighted_priorities["musicbrainz.release_group_id"] = (1e6, 1)

    if item.get("musicbrainz.artist_id", "a") == candidate.get(
        "musicbrainz.artist_id", "b"
    ):
        if "title" in candidate or "album" in candidate:
            weighted_priorities["musicbrainz.artist_id"] = (1e4, 1)
        else:
            weighted_priorities["musicbrainz.artist_id"] = (1e6, 1)

    return candidate


def _annotate_spotify(item: Item, candidate: Item) -> Item:
    """
    Annotate priorities based on spotify IDs.

    Depending on whether candidate is a track, an album or an artist, the main
    weight is set to 1E6, similar to  similarity.isrc in _annotate_similarity
    and all remaining weights are two decades smaller since they dont indicate
    perfect matches but imply that all other candidates should be neglected.
    """

    weighted_priorities = candidate.setdefault("_.weighted_priorities", dict())

    if item.get("spotify.id", "a") == candidate.get("spotify.id", "b"):
        weighted_priorities["spotify.id"] = (1e6, 1)

    if item.get("spotify.album_id", "a") == candidate.get("spotify.album_id", "b"):
        if "title" in candidate:
            weighted_priorities["spotify.album_id"] = (1e4, 1)
        else:
            weighted_priorities["spotify.album_id"] = (1e6, 1)

    if item.get("spotify.artist_id", "a") == candidate.get("spotify.artist_id", "b"):
        if "title" in candidate or "album" in candidate:
            weighted_priorities["spotify.artist_id"] = (1e4, 1)
        else:
            weighted_priorities["spotify.artist_id"] = (1e6, 1)

    return candidate
