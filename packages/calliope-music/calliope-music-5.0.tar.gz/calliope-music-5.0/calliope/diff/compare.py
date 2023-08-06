# Calliope
# Copyright (C) 2021  Sam Thursfield <sam@afuera.me.uk>
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

import enum
import logging

import calliope.playlist

log = logging.getLogger(__name__)


class PropertyState(enum.Enum):
    MISSING_BOTH = 0
    MISSING_A = 1
    MISSING_B = 2
    NOT_EQUAL = 3
    EQUAL = 4


def property_compare_exact(property_name: str,
                           a: calliope.playlist.Item,
                           b: calliope.playlist.Item) -> PropertyState:
    """True if ``property_name`` is present and exactly equal."""
    if property_name in a:
        if property_name in b:
            if a[property_name] == b[property_name]:
                result = PropertyState.EQUAL
            else:
                result = PropertyState.NOT_EQUAL
        else:
            result = PropertyState.MISSING_B
    elif property_name in b:
        result = PropertyState.MISSING_A
    else:
        result = PropertyState.MISSING_BOTH
    #log.debug("Comparing property %s in %s and %s: %s", property_name, a, b, result)
    return result


def property_compare_case_insensitive(property_name: str,
                                      a: calliope.playlist.Item,
                                      b: calliope.playlist.Item) -> PropertyState:
    """True if ``property_name`` is present and equal when lowercased."""
    if property_name in a:
        if property_name in b:
            if str(a[property_name]).lower() == str(b[property_name]).lower():
                result = PropertyState.EQUAL
            else:
                result = PropertyState.NOT_EQUAL
        else:
            result = PropertyState.MISSING_B
    elif property_name in b:
        result = PropertyState.MISSING_A
    else:
        result = PropertyState.MISSING_BOTH
    #log.debug("Comparing property %s in %s and %s: %s", property_name, a, b, result)
    return result


def creator_equal(a: calliope.playlist.Item, b: calliope.playlist.Item):
    """True if creator (artist) of ``a`` and ``b`` are the same.

    Considers properties:

        * ``musicbrainz.artist_id``
        * ``creator`` (case insensitive)

    """
    musicbrainz_artist_id_state = property_compare_exact('musicbrainz.artist_id', a, b)
    if musicbrainz_artist_id_state == PropertyState.EQUAL:
        return True
    elif musicbrainz_artist_id_state == PropertyState.NOT_EQUAL:
        return False

    creator_state = property_compare_case_insensitive('creator', a, b)
    if creator_state == PropertyState.EQUAL:
        return True

    return False


def album_equal(a: calliope.playlist.Item, b: calliope.playlist.Item):
    """True if ``a`` and ``b`` represent the same album (release group).

    Considers properties:

        * ``musicbrainz.release_group_id``
        * ``musicbrainz.release_id``
        * ``album`` and ``creator`` (case insensitive)

    """
    musicbrainz_release_group_id_state = property_compare_exact('musicbrainz.release_group_id', a, b)
    if musicbrainz_release_group_id_state == PropertyState.EQUAL:
        return True
    elif musicbrainz_release_group_id_state == PropertyState.NOT_EQUAL:
        return False

    musicbrainz_release_id_state = property_compare_exact('musicbrainz.release_id', a, b)
    if musicbrainz_release_id_state == PropertyState.EQUAL:
        return True
    elif musicbrainz_release_id_state == PropertyState.NOT_EQUAL:
        return False

    album_state = property_compare_case_insensitive('album', a, b)
    creator_state = property_compare_case_insensitive('creator', a, b)
    if album_state == PropertyState.EQUAL:
        if creator_state == PropertyState.NOT_EQUAL:
            return False
        return True
    elif album_state == PropertyState.NOT_EQUAL:
        return False
    elif creator_state == PropertyState.EQUAL:
        return True

    return False


def song_equal(a: calliope.playlist.Item, b: calliope.playlist.Item):
    """True if ``a`` and ``b`` represent the same song (recording).

    Considers :meth:`creator_equal`, plus these properties properties:

        * ``identifier``
        * ``musicbrainz.recording_id``
        * ``title`` (case insensitive)

    """
    identifier_state = property_compare_exact('identifier', a, b)
    if identifier_state == PropertyState.EQUAL:
        return True
    elif identifier_state == PropertyState.NOT_EQUAL:
        return False

    musicbrainz_recording_id_state = property_compare_exact('musicbrainz.recording_id', a, b)
    if musicbrainz_recording_id_state == PropertyState.EQUAL:
        return True
    elif musicbrainz_recording_id_state == PropertyState.NOT_EQUAL:
        return False

    title_state = property_compare_case_insensitive('title', a, b)
    creator_equal_result = creator_equal(a, b)
    if title_state == PropertyState.EQUAL:
        return creator_equal_result
    elif title_state == PropertyState.NOT_EQUAL:
        return False

    return creator_equal_result


def track_equal(a: calliope.playlist.Item, b: calliope.playlist.Item):
    """True if ``a`` and ``b`` represent the same track on the same album.

    Considers :meth:`song_equal`, :meth:`album_equal`, plus these properties:

        * ``musicbrainz.track_id``
        * ``trackNum``

    """
    musicbrainz_track_id_state = property_compare_exact('musicbrainz.track_id', a, b)
    if musicbrainz_track_id_state == PropertyState.EQUAL:
        return True
    elif musicbrainz_track_id_state == PropertyState.NOT_EQUAL:
        return False

    trackNum_state = property_compare_exact('trackNum', a, b)
    if trackNum_state == PropertyState.NOT_EQUAL:
        return False

    return song_equal(a, b) and album_equal(a, b)
