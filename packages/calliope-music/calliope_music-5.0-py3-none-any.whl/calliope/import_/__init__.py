# Calliope
# Copyright (C) 2016,2020  Sam Thursfield <sam@afuera.me.uk>
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


"""Convert playlists from different serialization formats.

See also: :program:`cpe import` command.

"""

import yaml

import configparser
import logging
import xml.etree.ElementTree

import calliope.playlist

log = logging.getLogger(__name__)


class PlaylistReadError(Exception):
    """Exception raised if playlist parsing fails."""


def guess_format(text: str) -> calliope.playlist.PlaylistFormat:
    """Guess the format of the input playlist.

    This is a simple function which tries different parsers in succession
    until one succeeds. It's not the most efficient way to load a playlist.

    """
    try:
        log.debug("guess_format: Checking INI-style format (pls)")
        parser = configparser.ConfigParser()
        parser.read_string(text)
        if parser.has_section('playlist'):
            return calliope.playlist.PlaylistFormat.PLS
    except (UnicodeDecodeError, configparser.Error) as e:
        log.debug("guess_format: Got exception: %s", e)

    try:
        log.debug("guess_format: Checking XML format (xspf)")
        tree = xml.etree.ElementTree.fromstring(text)
        if tree.tag == '{http://xspf.org/ns/0/}playlist':
            return calliope.playlist.PlaylistFormat.XSPF
    except xml.etree.ElementTree.ParseError as e:
        log.debug("guess_format: Got exception: %s", e)

    try:
        log.debug("guess_format: Checking YAML / JSON format (jspf)")
        # JSON is a subset of YAML, so we're just gonna try YAML here.
        doc = yaml.safe_load(text)
        if not isinstance(doc, dict) or len(doc) == 0:
            log.debug("guess_format: JSON/YAML parsing succeeded but the document is empty or not a dict.")
        elif 'playlist' in doc:
            return calliope.playlist.PlaylistFormat.JSPF
    except yaml.YAMLError as e:
        log.debug("guess_format: Got exception: %s", e)

    return None


def parse_pls(text: str) -> calliope.playlist.Playlist:
    """Parse playlist in PLS format."""
    parser = configparser.ConfigParser(interpolation=None)
    parser.read_string(text)
    number_of_entries = parser.getint('playlist', 'NumberOfEntries')

    entries = []
    for i in range(1, number_of_entries+1):
        entry = {
            'location': parser.get('playlist', 'File%i' % i),
            'title': parser.get('playlist', 'Title%i' % i)
        }
        entries.append(calliope.playlist.Item(entry))
    return entries


def parse_xspf(text: str) -> calliope.playlist.Playlist:
    """Parse playlist in XSPF format."""
    tree = xml.etree.ElementTree.fromstring(text)

    if tree.tag != '{http://xspf.org/ns/0/}playlist':
        raise PlaylistReadError("Invalid XSPF: No top-level <playlist> tag.")

    tracklist = tree.find('{http://xspf.org/ns/0/}trackList')
    if tracklist is None:
        raise PlaylistReadError("Invalid XSPF: No <trackList> section.")

    def xspf_tag_to_calliope_property(element, entry, tag, prop):
        first_child_element = element.find(tag)
        if first_child_element is not None:
            entry[prop] = first_child_element.text

    entries = []
    for track in tracklist:
        entry = {}

        # XSPF tracks can have multiple <location> and <identifier> tags.
        # We currently just use the first of each.
        xspf_tag_to_calliope_property(track, entry, '{http://xspf.org/ns/0/}location', 'location')
        xspf_tag_to_calliope_property(track, entry, '{http://xspf.org/ns/0/}identifier', 'identifier')

        # These tags shouldn't appear more than once. All are optional though.
        xspf_tag_to_calliope_property(track, entry, '{http://xspf.org/ns/0/}title', 'title')
        xspf_tag_to_calliope_property(track, entry, '{http://xspf.org/ns/0/}creator', 'creator')
        xspf_tag_to_calliope_property(track, entry, '{http://xspf.org/ns/0/}annotation', 'annotation')
        xspf_tag_to_calliope_property(track, entry, '{http://xspf.org/ns/0/}info', 'info')
        xspf_tag_to_calliope_property(track, entry, '{http://xspf.org/ns/0/}image', 'image')
        xspf_tag_to_calliope_property(track, entry, '{http://xspf.org/ns/0/}album', 'album')
        xspf_tag_to_calliope_property(track, entry, '{http://xspf.org/ns/0/}trackNum', 'trackNum')
        xspf_tag_to_calliope_property(track, entry, '{http://xspf.org/ns/0/}duration', 'duration')

        if 'duration' in entry:
            # Convert from milliseconds to seconds.
            entry['duration'] = int(entry['duration']) / 1000.0

        # We currently ignore the <link>, <meta> and <extension> tags.

        if len(entry) == 0:
            log.warning("Empty <track> entry found.")

        entries.append(calliope.playlist.Item(entry))

    if len(entries) > 0:
        # If the playlist has metadata tags, we store them on the first entry
        # that we return.
        metadata_entry = entries[0]
        xspf_tag_to_calliope_property(tree, metadata_entry, '{http://xspf.org/ns/0/}title', 'playlist.title')
        xspf_tag_to_calliope_property(tree, metadata_entry, '{http://xspf.org/ns/0/}creator', 'playlist.creator')
        xspf_tag_to_calliope_property(tree, metadata_entry, '{http://xspf.org/ns/0/}annotation', 'playlist.annotation')
        xspf_tag_to_calliope_property(tree, metadata_entry, '{http://xspf.org/ns/0/}info', 'playlist.info')
        xspf_tag_to_calliope_property(tree, metadata_entry, '{http://xspf.org/ns/0/}location', 'playlist.location')
        xspf_tag_to_calliope_property(tree, metadata_entry, '{http://xspf.org/ns/0/}identifier', 'playlist.identifier')
        xspf_tag_to_calliope_property(tree, metadata_entry, '{http://xspf.org/ns/0/}image', 'playlist.image')
        xspf_tag_to_calliope_property(tree, metadata_entry, '{http://xspf.org/ns/0/}date', 'playlist.date')
        xspf_tag_to_calliope_property(tree, metadata_entry, '{http://xspf.org/ns/0/}license', 'playlist.license')

        # We currently ignore the <attribution> and <link> tags.

    return entries


def jspf_to_calliope(jspf_entry, calliope_entry, jspf_property, calliope_property):
    if jspf_property in jspf_entry:
        calliope_entry[calliope_property] = jspf_entry[jspf_property]


JSPF_EXTENSION_LISTENBRAINZ_PLAYLIST = "https://musicbrainz.org/doc/jspf#playlist"
JSPF_EXTENSION_LISTENBRAINZ_TRACK = "https://musicbrainz.org/doc/jspf#track"


def process_jspf_listenbrainz_playlist_extension(extension, entry):
    jspf_to_calliope(extension, entry, 'created_for', 'listenbrainz.playlist.created_for')
    jspf_to_calliope(extension, entry, 'creator', 'listenbrainz.playlist.creator')
    jspf_to_calliope(extension, entry, 'collaborators', 'listenbrainz.playlist.collaborators')
    jspf_to_calliope(extension, entry, 'copied_from', 'listenbrainz.playlist.copied_from')
    jspf_to_calliope(extension, entry, 'copied_from_deleted', 'listenbrainz.playlist.copied_from_deleted')
    jspf_to_calliope(extension, entry, 'public', 'listenbrainz.playlist.public')
    jspf_to_calliope(extension, entry, 'last_modified_at', 'listenbrainz.playlist.last_modified_at')
    jspf_to_calliope(extension, entry, 'algorithm_metadata', 'listenbrainz.playlist.algorithm_metadata')


def process_jspf_listenbrainz_track_extension(extension, entry):
    jspf_to_calliope(extension, entry, 'added_by', 'listenbrainz.added_by')
    # artist_mbids is not used due to https://tickets.metabrainz.org/browse/LB-1058
    # even though as of 2022-02-13 the still says artist_mbids
    jspf_to_calliope(extension, entry, 'artist_identifiers', 'listenbrainz.artist_identifiers')
    jspf_to_calliope(extension, entry, 'release_identifier', 'listenbrainz.release_identifier')


def parse_jspf(text: str) -> calliope.playlist.Playlist:
    """Parse playlist in JSPF format."""
    doc = yaml.safe_load(text)
    return process_jspf(doc)


def process_jspf(doc) -> calliope.playlist.Playlist:
    if 'playlist' not in doc:
        raise PlaylistReadError("Invalid XSPF: No top-level 'playlist' item.")
    playlist = doc['playlist']

    if 'track' not in playlist:
        raise PlaylistReadError("Invalid XSPF: No 'track' list.")
    tracklist = playlist['track']

    entries = []
    for track in tracklist:
        entry = {}

        jspf_to_calliope(track, entry, 'location', 'location')
        jspf_to_calliope(track, entry, 'identifier', 'identifier')

        # XSPF tracks can have multiple <location> and <identifier> tags.
        # We currently just use the first of each.
        if 'location' in entry and isinstance(entry['location'], list):
            entry['location'] = entry['location'][0]
        if 'identifier' in entry and isinstance(entry['identifier'], list):
            entry['identifier'] = entry['identifier'][0]

        # These tags shouldn't appear more than once. All are optional though.
        jspf_to_calliope(track, entry, 'title', 'title')
        jspf_to_calliope(track, entry, 'creator', 'creator')
        jspf_to_calliope(track, entry, 'annotation', 'annotation')
        jspf_to_calliope(track, entry, 'info', 'info')
        jspf_to_calliope(track, entry, 'image', 'image')
        jspf_to_calliope(track, entry, 'album', 'album')
        jspf_to_calliope(track, entry, 'trackNum', 'trackNum')
        jspf_to_calliope(track, entry, 'duration', 'duration')

        if 'duration' in entry:
            # Convert from milliseconds to seconds.
            entry['duration'] = int(entry['duration']) / 1000.0

        extension = track.get('extension', {})
        if JSPF_EXTENSION_LISTENBRAINZ_TRACK in extension:
            process_jspf_listenbrainz_track_extension(
                extension[JSPF_EXTENSION_LISTENBRAINZ_TRACK], entry)

        # We currently ignore the <link>, and <meta> tags.

        if len(entry) == 0:
            log.warning("Empty 'track' entry found.")

        entries.append(calliope.playlist.Item(entry))

    if len(entries) > 0:
        # If the playlist has metadata tags, we store them on the first entry
        # that we return.
        metadata_entry = entries[0]
        jspf_to_calliope(playlist, metadata_entry, 'title', 'playlist.title')
        jspf_to_calliope(playlist, metadata_entry, 'creator', 'playlist.creator')
        jspf_to_calliope(playlist, metadata_entry, 'annotation', 'playlist.annotation')
        jspf_to_calliope(playlist, metadata_entry, 'info', 'playlist.info')
        jspf_to_calliope(playlist, metadata_entry, 'location', 'playlist.location')
        jspf_to_calliope(playlist, metadata_entry, 'identifier', 'playlist.identifier')
        jspf_to_calliope(playlist, metadata_entry, 'image', 'playlist.image')
        jspf_to_calliope(playlist, metadata_entry, 'date', 'playlist.date')
        jspf_to_calliope(playlist, metadata_entry, 'license', 'playlist.license')

        extension = playlist.get('extension', {})
        if JSPF_EXTENSION_LISTENBRAINZ_PLAYLIST in extension:
            process_jspf_listenbrainz_playlist_extension(
                extension[JSPF_EXTENSION_LISTENBRAINZ_PLAYLIST], metadata_entry)

        # We currently ignore the <attribution> and <link> tags.

    return entries


def import_(text: str) -> calliope.playlist.Playlist:
    """Parse playlist data from a file.

    The type of the input data will be autodetected. The supported formats are:
    PLS, XSPF, JSPF.

    Args:
        text: The file contents.

    Returns:
        A playlist.
    """

    playlist_format = guess_format(text)

    if not playlist_format:
        raise RuntimeError("Could not determine the input format.")
    elif playlist_format == calliope.playlist.PlaylistFormat.PLS:
        entries = parse_pls(text)
    elif playlist_format == calliope.playlist.PlaylistFormat.XSPF:
        entries = parse_xspf(text)
    elif playlist_format == calliope.playlist.PlaylistFormat.JSPF:
        entries = parse_jspf(text)

    return entries
