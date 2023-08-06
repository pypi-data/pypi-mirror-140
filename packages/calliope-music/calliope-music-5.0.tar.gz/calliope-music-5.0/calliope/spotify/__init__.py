# Calliope
# Copyright (C) 2017,2020  Sam Thursfield <sam@afuera.me.uk>
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


"""Access data from the `Spotify music streaming service <https://www.spotify.com>`_.

This module wraps the `Spotipy <https://spotipy.readthedocs.io/>`_ library.

Authentication
--------------

You will need a :ref:`Spotify API key <api-keys.spotify>` to authenticate with
Spotify.  The credentials should be provided via a
:class:`calliope.config.Configuration` instance when creating the
:class:`calliope.spotify.SpotifyContext`.

The first time :func:`calliope.spotify.SpotifyContext.authenticate` is called,
it will open a browser window to authorize with Spotify, and will return the
access token via a `local HTTP server <https://github.com/plamere/spotipy/pull/243/>`_
or by asking to paste the redirected URI::

    $ cpe spotify export
    Couldn't read cache at: /home/sam/.cache/calliope/spotify/credentials.json
    Enter the URL you were redirected to:

The authorization code will be saved in the cache so future API access will
work without a prompt, until the cached code expires.

Caching
-------

By default, all new HTTP requests are saved to disk. Cache expiry is done
following ``etags`` and ``cache-control`` headers provided by the Spotify API.
"""

import itertools
import logging
import sys
from functools import partial
from math import floor
from pprint import pformat
from typing import Callable, Dict, Iterable, List, Optional

import cachecontrol
import cachecontrol.caches
import requests
import spotipy
import spotipy.util
from spotipy import Spotify

import calliope.cache
import calliope.config
import calliope.playlist
from calliope.playlist import Item
from calliope.resolvers import select_best
from calliope.utils import (
    FeatMode,
    drop_none_values,
    get_isrcs,
    get_nested,
    normalize_creator_title,
    parse_sort_date,
)

log = logging.getLogger(__name__)


class SpotifyContext():
    def __init__(self, config: calliope.config.Configuration, caching:
                 bool=True):
        """Context for accessing Spotify Web API.

        The :meth:`authenticate` function must be called to obtain a
        :class:`spotipy.client.Spotify` object.

        Args:
            config: Provides ``spotify.client_id``, ``spotify.client_secret`` and ``spotify.redirect_uri``
            caching: Enables caching to ``$XDG_CACHE_HOME/calliope/spotify``

        """
        self.config = config
        self.caching = caching

        self.api = None

    def _get_session(self):
        session = requests.Session()
        if self.caching:
            cache_path = calliope.cache.save_cache_path('calliope/spotify')
            filecache = cachecontrol.caches.FileCache(cache_path.joinpath('webcache'))
            session.mount('https://api.spotify.com/',
                          cachecontrol.CacheControlAdapter(cache=filecache))
        return session

    def authenticate(self) -> spotipy.client.Spotify:
        """Authenticate against the Spotify API.

        See above for details on how this works.

        """
        client_id = self.config.get('spotify', 'client-id')
        client_secret = self.config.get('spotify', 'client-secret')
        redirect_uri = self.config.get('spotify', 'redirect-uri')

        scope = (
            "playlist-read-private,playlist-modify-private,"
            "user-top-read,"
            "user-library-read,user-library-modify,"
            "user-follow-read,user-follow-modify"
        )

        try:
            cache_path = calliope.cache.save_cache_path('calliope/spotify')
            credentials_cache_path = cache_path.joinpath('credentials.json')
            auth_manager = spotipy.oauth2.SpotifyOAuth(
                scope=scope, client_id=client_id, client_secret=client_secret,
                redirect_uri=redirect_uri, cache_path=credentials_cache_path)
            self.api = spotipy.Spotify(auth_manager=auth_manager,
                                       requests_session=self._get_session())
        except spotipy.client.SpotifyException as e:
            raise RuntimeError(e) from e

        self.api.trace = False


def _sp_tracks_to_items(sp_tracks: Iterable[Dict]) -> Iterable[Item]:
    """
    Convert spotify track dicts into calliope playlist items.

    The returned items can be passed into resolvers.py. Spotify specific
    fields are prefixed with "spotify." and fields that should not be visible
    to a user are prefixed with "_.". As many non-dotted fields are filled
    as possible.

    Args:
        sp_tracks: An Iterable of spotify track dicts

    Returns:
        A calliope Item Iterator
    """

    seen = set()
    for sp_track in sp_tracks:
        if sp_track["id"] in seen:
            continue

        sp_artist = get_nested(sp_track, ("artists", 0))
        sp_album = sp_track["album"]

        item = Item(
            data={
                "spotify.title": sp_track.get("name"),
                "spotify.album": sp_album.get("name"),
                "spotify.artist": sp_artist.get("name"),
                "spotify.duration_ms": float(sp_track["duration_ms"]),
                "spotify.albumartist": get_nested(sp_album, ("artists", 0, "name")),
                "spotify.album_id": sp_album.get("id"),
                "spotify.id": sp_track["id"],
                "spotify.artist_id": sp_artist.get("id"),
                "spotify.date": sp_album.get("release_date"),
                "spotify.isrc": get_nested(sp_track, ("external_ids", "isrc")),
                "spotify.popularity": sp_track["popularity"],
                "_.secondary-type-list": [sp_album.get("album_type")]
                if sp_album.get("album_type") is not None
                else [],
                "_.medium-track-count": sp_album.get("total_tracks"),
                "_.sort_date": parse_sort_date(sp_album.get("release_date")),
            }
        )
        seen.add(sp_track["id"])

        for src, dst in (
            ("spotify.title", "title"),
            ("spotify.album", "album"),
            ("spotify.artist", "creator"),
            ("spotify.duration_ms", "duration"),
            ("spotify.albumartist", "_.albumartist"),
            ("spotify.date", "_.date"),
        ):
            item[dst] = item[src]

        yield drop_none_values(item)


def _sp_albums_to_items(sp_albums: Iterable[Dict]) -> Iterable[Item]:
    """
    Convert spotify album dicts into calliope playlist items.

    The returned items can be passed into resolvers.py. Spotify specific
    fields are prefixed with "spotify." and fields that should not be visible
    to a user are prefixed with "_.". As many non-dotted fields are filled
    as possible.

    Args:
        sp_albums: An Iterable of spotify album dicts

    Returns:
        A calliope Item Iterator
    """
    seen = set()
    for sp_album in sp_albums:
        if sp_album["id"] in seen:
            continue

        sp_artist = get_nested(sp_album, ("artists", 0))

        item = Item(
            data={
                "spotify.album": sp_album.get("name"),
                "spotify.albumartist": sp_artist.get("name"),
                "spotify.album_id": sp_album.get("id"),
                "spotify.artist_id": sp_artist.get("id"),
                "spotify.date": sp_album.get("release_date"),
                "_.secondary-type-list": [sp_album.get("album_type")]
                if sp_album.get("album_type") is not None
                else [],
                "_.medium-track-count": sp_album.get("total_tracks"),
                "_.sort_date": parse_sort_date(sp_album.get("release_date")),
            }
        )
        seen.add(sp_album["id"])

        for src, dst in (
            ("spotify.album", "album"),
            ("spotify.albumartist", "creator"),
            ("spotify.albumartist", "_.albumartist"),
            ("spotify.date", "_.date"),
        ):
            item[dst] = item[src]

        yield drop_none_values(item)


def _sp_artists_to_items(sp_artists: Iterable[Dict]) -> Iterable[Item]:
    """
    Convert spotify artist dicts into calliope playlist items.

    The returned items can be passed into resolvers.py. Spotify specific
    fields are prefixed with "spotify." and fields that should not be visible
    to a user are prefixed with "_.". As many non-dotted fields are filled
    as possible.

    Args:
        sp_artists: An Iterable of spotify artist dicts

    Returns:
        A calliope Item Iterator
    """
    seen = set()
    for sp_artist in sp_artists:
        if sp_artist["id"] in seen:
            continue

        item = Item(
            data={
                "creator": sp_artist.get("name"),
                "spotify.artist": sp_artist.get("name"),
                "spotify.artist_id": sp_artist.get("id"),
            }
        )
        seen.add(sp_artist["id"])

        yield drop_none_values(item)


def _build_queries(item: Item) -> Iterable[str]:
    """
    Build and return spotify queries from an existing playlist item.

    This function can be used to search for tracks, albums and artists. Different
    query strings are yielded with descending precision.

    Args:
        item: An Item for which a spotify match is sought

    Returns:
        A query string which canbe passed into Spotify.search()

    """

    isrcs = get_isrcs(item)
    for isrc in set(isrcs):
        yield f"isrc:{isrc}"

    title = item.get("title")
    creator = item.get("creator")
    creator, title = normalize_creator_title(creator, title, feat_mode=FeatMode.DROP)
    album = item.get("album")

    query = dict()
    if title is not None:
        query["track"] = title
    if creator is not None:
        query["artist"] = creator
    if album is not None and title is None:
        query["album"] = album

    yield " ".join([f"{k}:{v}" for k, v in query.items()])
    yield " ".join(query.values())
    if "artist" in query:
        yield query["artist"]
    if "album" in query:
        yield query["album"]
    if "track" in query:
        yield query["track"]


def _search(
    api: spotipy.Spotify,
    cache,
    item: Item,
    select_func: Callable[[Item, List[Item]], Optional[Item]] = select_best,
) -> Optional[Item]:
    """
    Search Spotify for the best match of item.

    Args:
        api: A Spotify instance
        cache: A calliope Cache instance
        item: The item to search the match for
        select_func: A selector function which chooses the best match from the
            retrieved candidates

    Returns:
        The match or None in case no good match was found.
    """

    candidates = []
    for query_str in _build_queries(item):
        if "title" in item:
            sp_tracks = cache.wrap(
                query_str,
                partial(
                    _search_paginated, api=api, query_str=query_str, item_type="track"
                ),
            )
            candidates.extend(_sp_tracks_to_items(sp_tracks))
        elif "album" in item:
            sp_albums = cache.wrap(
                query_str,
                partial(
                    _search_paginated, api=api, query_str=query_str, item_type="album"
                ),
            )
            candidates.extend(_sp_albums_to_items(sp_albums))
        elif "creator" in item:
            sp_artists = cache.wrap(
                query_str,
                partial(
                    _search_paginated, api=api, query_str=query_str, item_type="artist"
                ),
            )
            candidates.extend(_sp_artists_to_items(sp_artists))
        else:
            raise KeyError()

        if len(candidates) >= 20:
            break

    if len(candidates) == 0:
        log.warning("Unable to find item on spotify: {}".format(item))
        return None

    log.debug("Found {} candidates for item {}".format(len(candidates), repr(item)))
    match = select_func(item, candidates)

    return match


def _search_paginated(
    api,
    query_str: str,
    item_type: str = "track",
    result_count_limit=300,
):
    """
    Search spotify using a the specified query string an item type and
    return as many results as result_count_limit permits.

    Args:
        query_str: A query string to pass into Spotify.search()
        item_type: The spotify item type to search for, accepts track,
            artist and album

    Returns:
        A list of dicts returned by Spotify.search()

    """
    item_types = item_type + "s"
    items: List[Dict] = []
    offset = 0
    while len(items) < result_count_limit:
        response = api.search(
            q=query_str,
            type=item_type,
            limit=50,
            offset=offset,
        )
        items.extend(i for i in response[item_types]["items"])
        if response[item_types].get("next") is None:
            break
        offset += 50

    return items


def resolve(
    api: spotipy.Spotify, playlist: calliope.playlist.Playlist, select_func=None, update=False
) -> Iterable[calliope.playlist.Item]:
    cache = calliope.cache.open(namespace="spotify")
    for item in playlist:
        match = _search(api, cache, item, select_func=select_func)
        if match is not None:
            for key, v in match.items():
                if key.startswith("spotify.") or (update and "." not in key):
                    item[key] = v
            item["calliope.spotify.resolver_score"] = match["_.priority"]
        yield item


def _export_spotify_playlist(playlist, tracks):
    playlist_metadata = {
        'playlist.title': playlist['name'],
    }

    playlist_info_url = playlist['external_urls'].get('spotify')
    if playlist_info_url:
        playlist_metadata['playlist.location'] = playlist_info_url

    for i, track in enumerate(tracks['items']):
        item = {
            'title': track['track']['name'],
            'creator': track['track']['artists'][0]['name'],
        }

        location = track['track']['external_urls'].get('spotify')
        if location:
            item['location'] = location

        if i == 0:
            item.update(playlist_metadata)

        yield item


def export(spotify: SpotifyContext, user_id: str = None):
    """Export all playlists for given user.

    Args:
        user_id: Optional, defaults to authenticated user.
    """
    sp = spotify.api
    user_id = user_id or sp.current_user()['id']

    playlists = sp.current_user_playlists()
    for playlist in playlists['items']:
        if playlist['owner']['id'] == user_id:
            tracks = sp.user_playlist_tracks(user_id, playlist_id=playlist['id'])
            calliope.playlist.write(_export_spotify_playlist(playlist, tracks), stream=sys.stdout)


def export_library_tracks(spotify: SpotifyContext):
    """Export all library tracks for the current user"""
    api = spotify.api

    response = api.current_user_saved_tracks()
    tracks = [i["track"] for i in response["items"]]
    while response["next"] is not None:
        response = api.next(response)
        tracks.extend(i["track"] for i in response["items"])
    items = _sp_tracks_to_items(tracks)

    _export_library_items(items, "track")


def export_library_albums(spotify: SpotifyContext):
    """Export all library albums for the current user"""
    api = spotify.api

    response = api.current_user_saved_albums()
    albums = [i["album"] for i in response["items"]]
    while response["next"] is not None:
        response = api.next(response)
        albums.extend(i["album"] for i in response["items"])
    items = _sp_albums_to_items(albums)

    _export_library_items(items, "album")


def export_library_artists(spotify: SpotifyContext):
    """Export all library artists for the current user"""
    api = spotify.api

    response = api.current_user_followed_artists()
    artists = response["artists"]["items"]
    while response["artists"]["next"] is not None:
        response = api.next(response)
        artists.extend(response["artists"]["items"])
    items = _sp_artists_to_items(artists)

    _export_library_items(items, "artist")


def _export_library_items(items: Iterable[Item], item_type: str):
    items = (
        Item({k: v for k, v in ii.items() if not k.startswith("_")}) for ii in items
    )
    try:
        first_item = next(items)
    except StopIteration:
        return
    first_item["playlist.title"] = f"Spotify user library {item_type}s"

    items = itertools.chain([first_item], items)
    calliope.playlist.write(items, stream=sys.stdout)


def _as_chunks(iterable, chunksize):
    iterator = iter(iterable)
    while True:
        chunk = list(itertools.islice(iterator, chunksize))
        if len(chunk) == 0:
            break
        yield chunk


def import_library(
    context: SpotifyContext,
    playlist: calliope.playlist.Playlist,
):
    """Import items into the current user's spotify library. Supported types are
    tracks, albums and artists.
    """
    api: Spotify = context.api

    track_items = {}
    album_items = {}
    artist_items = {}

    for item in playlist:
        if "spotify.id" in item:
            track_items[item["spotify.id"]] = item
        elif "spotify.album_id" in item:
            album_items[item["spotify.album_id"]] = item
        elif "spotify.artist_id" in item:
            artist_items[item["spotify.artist_id"]] = item
        elif "spotify.uri" in item:
            sp_uri = item["spotify.uri"]
            if sp_uri.startswith("spotify:track:"):
                track_items[item["spotify.uri"]] = item
            elif sp_uri.startswith("spotify:album:"):
                album_items[item["spotify.uri"]] = item
            elif sp_uri.startswith("spotify:artist:"):
                artist_items[item["spotify.uri"]] = item
            else:
                log.warning("Invalid spotify URI: {}".format(item))
        else:
            log.warning(
                "no spotify.id, spotify.album_id, spotify.artist_id or spotify.uri"
                " fields found in item {}, please use annotate first".format(item)
            )

    _import_items(track_items, api.current_user_saved_tracks_add)
    _import_items(album_items, api.current_user_saved_albums_add)
    _import_items(artist_items, api.user_follow_artists)


def _import_items(id_to_items: Dict[str, Item], import_func: Callable):
    """
    Import items into the current user's spotify library as chunks.

    Invalid spotify IDs (which may occur e.g. due to market restrictions) are
    ignored and logged at the end.

    Args:
        id_to_items: A dict of items to export with their spotify ids as keys.
        import_func: the spotify api function to use for importing, e.g.
            current_user_saved_tracks_add

    """

    sp_ids = list(id_to_items.keys())
    chunk_size = 32
    # we start with a chunk size of 32 and shrink it down to 1 to until all
    # valid spotify IDs are imported, popping the imported IDs from sp_ids.
    while len(sp_ids) > 0 and chunk_size > 0:
        for sp_id_chunk in _as_chunks(sp_ids, chunk_size):
            try:
                import_func(sp_id_chunk)
                for sp_id in sp_id_chunk:
                    sp_ids.remove(sp_id)
            except spotipy.exceptions.SpotifyException:
                pass
        chunk_size = floor(chunk_size / 2)

    if len(sp_ids) > 0:
        log.error(
            "could not add items:\n\t{}".format(
                "\n\t".join(str(id_to_items[k]) for k in sp_ids)
            )
        )


def import_(
    context: SpotifyContext,
    playlist: calliope.playlist.Playlist,
    user_id: Optional[str] = None,
):
    """Import a playlist to Spotify.

    Args:
        user_id: Optional, defaults to authenticated user. Requires
                 appropriate permissions.

    """
    api: Spotify = context.api
    user_id = user_id or api.current_user()["id"]

    first_item = next(playlist)

    if "playlist.title" in first_item:
        playlist_name = first_item["playlist.title"]
    else:
        raise RuntimeError("No playlist.title found in playlist")

    sp_playlist = _find_sp_playlist(context=context, user=user_id, name=playlist_name)
    if sp_playlist is not None:
        log.debug("overwriting existing playlist {}".format(sp_playlist["name"]))
    else:
        sp_playlist = api.user_playlist_create(
            user=user_id, name=playlist_name, public=False, collaborative=False
        )
        log.debug("created new playlist {}".format(sp_playlist["name"]))

    sp_urls = []
    for item in itertools.chain([first_item], playlist):
        if 'spotify.uri' in item:
            sp_urls.append(item["spotify.uri"])
        elif 'spotify.id' in item:
            sp_urls.append(f'https://open.spotify.com/track/{item["spotify.id"]}')
        else:
            log.warning(
                "no spotify.id or spotify.uri fields found in track {}, please use resolve first".format(
                    item
                )
            )

    log.debug("adding new tracks {}".format(pformat(sp_urls)))
    api.playlist_replace_items(playlist_id=sp_playlist["id"], items=sp_urls)


def _find_sp_playlist(context: SpotifyContext, name: str, user=None) -> Optional[Dict]:
    user = context.api.current_user()["id"] if user is None else user
    offset = 0
    while True:
        resp = context.api.user_playlists(user=user, limit=50, offset=offset)
        for item in resp["items"]:
            if item["name"] == name:
                return item
        if resp["next"] is None:
            break
        offset += 50

    return None


def top_artists(spotify: SpotifyContext, count: int, time_range: str) -> calliope.playlist.Playlist:
    """Return top artists for the authenticated user."""
    sp = spotify.api
    response = sp.current_user_top_artists(limit=count, time_range=time_range)['items']

    if count > 50:
        # This is true as of 2018-08-18; see:
        # https://developer.spotify.com/documentation/web-api/reference/personalization/get-users-top-artists-and-tracks/
        raise RuntimeError("Requested {} top artists, but the Spotify API will "
                           "not return more than 50.".format(count))

    output = []
    for i, artist_info in enumerate(response):
        output_item = {
            'creator': artist_info['name'],
            'spotify.artist_id': artist_info['id'],
            'spotify.creator_user_ranking': i+1,
            'spotify.creator_image': artist_info['images']
        }
        output.append(output_item)

    return output
