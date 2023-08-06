# Calliope
# Copyright (C) 2016,2018,2020  Sam Thursfield <sam@afuera.me.uk>
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


"""Export data from the `Tracker desktop search engine <gnome.pages.gitlab.gnome.org/tracker/>`_.

See also: :program:`cpe tracker` command.

"""

import gi

try:
    gi.require_version('MediaArt', '2.0')
    gi.require_version('Tracker', '3.0')
    from gi.repository import MediaArt, Tracker     # pylint: disable=no-name-in-module
except ValueError as e:
    raise ImportError(e) from e

import calliope.playlist

import logging
import pathlib
import urllib.parse

log = logging.getLogger(__name__)

TRACKER_INDEXER = 'org.freedesktop.Tracker3.Miner.Files'


def _escape(s):
    return Tracker.sparql_escape_string(s)


class TrackerClient():
    """Helper functions for querying from the user's Tracker database."""

    def __init__(self, http_endpoint=None):
        if http_endpoint:
            self._conn = Tracker.SparqlConnection.remote_new(http_endpoint)
        else:
            self._conn = Tracker.SparqlConnection.bus_new(TRACKER_INDEXER, None, None)

        self._stmt_cache = {}

    def query(self, query: str) -> Tracker.SparqlCursor:
        '''Run a single SPARQL query.'''
        log.debug("Query: %s" % query)
        return self._conn.query(query)

    def _prepare(self, name, sparql):
        if name not in self._stmt_cache:
            self._stmt_cache[name] = self._conn.query_statement(sparql, None)
        return self._stmt_cache[name]

    def artist_id(self, artist_name: str) -> str:
        '''Return the Tracker URN for a given artist.'''

        query_artist_urn = """
        SELECT ?u FROM tracker:Audio {
            ?u a nmm:Artist ;
                dc:title ?name .
            FILTER (LCASE(?name) = "~name_lower")
        }"""
        stmt = self._prepare('artist-urn', query_artist_urn)

        stmt.bind_string("name_lower", artist_name.lower())
        result = stmt.execute()

        if result.next():
            return result.get_string(0)[0]
        else:
            return None

    def artist_name(self, artist_id: str) -> str:
        '''Return the name of a given artist.'''

        query_artist_name = """
        SELECT ?name FROM tracker:Audio {
            ~uri a nmm:Artist ; dc:title ?name
        }"""
        stmt = self._prepare('artist-name', query_artist_name)

        stmt.bind_string("uri", artist_id)
        result = stmt.execute()

        if result.next():
            return result.get_string(0)[0]
        else:
            return None

    def artists_by_number_of_songs(self, limit: int=None):
        '''Return a list of artists by number of songs known.'''
        query_artists_by_number_of_songs = """
        SELECT ?artist_name (COUNT(?song) as ?songs) FROM tracker:Audio
          { ?artist a nmm:Artist ;
                dc:title ?artist_name .
            ?song nmm:artist ?artist }
        GROUP BY ?artist ORDER BY DESC(?songs) ?artist_name
        """

        if limit is not None:
            query = query_artists_by_number_of_songs + " LIMIT %i" % limit
        else:
            query = query_artists_by_number_of_songs

        cursor = self.query(query)

        while cursor.next():
            artist_name = cursor.get_string(0)[0]
            n_songs = cursor.get_string(1)[0]
            yield {
                'artist': artist_name,
                'track-count': n_songs
            }

    def albums(self, filter_artist_name: str=None, filter_album_name: str=None):
        '''Return a list of releases.'''

        if filter_artist_name:
            artist_pattern = 'FILTER (LCASE(?artist_name) = "%s")' % \
                _escape(filter_artist_name.lower())
        else:
            artist_pattern =" "

        if filter_album_name:
            album_pattern = 'FILTER (LCASE(?album_title) = "%s")' % \
                 _escape(filter_album_name.lower())
        else:
            album_pattern = ""

        query_albums = """
        SELECT
            ?artist_name ?album_title
            ?file AS ?first_file
            COUNT(?track) AS ?track_count
            SUM(nie:byteSize(?file)) / (1024.0 * 1024.0) AS ?size_mb
            SUM(nfo:duration(?track)) AS ?duration
        FROM tracker:Audio
        FROM tracker:FileSystem
        WHERE {
            ?album a nmm:MusicAlbum ;
              dc:title ?album_title ;
              nmm:albumArtist ?album_artist .
            ?album_artist nmm:artistName ?artist_name .
            ?track nmm:musicAlbum ?album ;
              nie:isStoredAs ?file .
            %s %s
        }
        GROUP BY ?album
        ORDER BY ?artist_name ?album_name
        """ % (artist_pattern, album_pattern)

        count = 0
        albums = self.query(query_albums)
        while albums.next():
            log.debug("Got 1 result")
            track_uri = albums.get_string(2)[0]
            track_path = urllib.parse.unquote(urllib.parse.urlparse(track_uri).path)
            album_path = pathlib.Path(track_path).parent
            yield {
                'creator': albums.get_string(0)[0],
                'album': albums.get_string(1)[0],
                'location': album_path.as_uri(),
                'tracker.location': album_path.as_uri(),
                'album.trackcount': albums.get_integer(3),
                'tracker.size_mb': round(albums.get_double(4)),
                'duration': albums.get_integer(5) * 1000,
            }
            count += 1
        log.debug("Got %i results", count)

    def track(self, artist_name: str, track_name: str) -> calliope.playlist.Item:
        '''Find a specific track by name.

        Tries to find a track matching the given artist and title.

        Returns a playlist entry, or None.

        '''
        query_track = r"""
        SELECT
            ?file
            nfo:duration(?track) AS ?duration
        FROM tracker:Audio
        WHERE {
            ?track a nmm:MusicPiece ;
              dc:title ?title ;
              nie:isStoredAs ?file ;
              nmm:artist ?artist .
            ?artist nmm:artistName ?artist_name .
            FILTER (fn:replace(LCASE(?title), "\\p{P}", "") = fn:replace(LCASE(~title), "\\p{P}", "") &&
                    fn:replace(LCASE(?artist_name), "\\p{P}", "") = fn:replace(LCASE(~artist), "\\p{P}", ""))
        }"""
        # The regex above is to strip punctuation, see
        # https://gitlab.gnome.org/GNOME/tracker/-/issues/274

        stmt = self._prepare('query-track', query_track)

        stmt.bind_string('title', track_name)
        stmt.bind_string('artist', artist_name)
        cursor = stmt.execute()

        if cursor.next():
            return calliope.playlist.Item({
                'title': track_name,
                'creator': artist_name,
                'location': cursor.get_string(0)[0],
                'tracker.location': cursor.get_string(0)[0],
                'duration': cursor.get_integer(1) * 1000,
            })
        else:
            return calliope.playlist.Item()

    def tracks(self, filter_artist_name: str=None,
               filter_album_name: str=None) -> calliope.playlist.Playlist:
        '''Return a list of tracks.'''

        if filter_artist_name:
            artist_pattern = 'FILTER (LCASE(?artist_name) = "%s")' % \
                _escape(filter_artist_name.lower())
        else:
            artist_pattern =" "

        if filter_album_name:
            album_pattern = """
                ?track nmm:musicAlbum [ nie:title ?albumTitle ] .
                FILTER (LCASE(?albumTitle) = "%s")
            """  % _escape(filter_album_name.lower())
        else:
            album_pattern = 'BIND ("" AS ?albumTitle)'

        query_tracks = """
        SELECT
            ?track_title ?file ?artist_name
            nie:byteSize(?file) / (1024.0 * 1024.0) AS ?size_mb
            nfo:duration(?track) AS ?duration
            ?albumTitle
        FROM tracker:Audio
        FROM tracker:FileSystem
            WHERE {
            ?track a nmm:MusicPiece ;
              dc:title ?track_title ;
              nie:isStoredAs ?file ;
              nmm:artist ?artist .
            ?artist nmm:artistName ?artist_name .
            %s %s
        }
        ORDER BY ?track_title ?artist_name
        """ % (artist_pattern, album_pattern)

        count = 0
        tracks = self.query(query_tracks)
        while tracks.next():
            log.debug("Got 1 result")
            item = calliope.playlist.Item({
                'title': tracks.get_string(0)[0],
                'creator': tracks.get_string(2)[0],
                'location': tracks.get_string(1)[0],
                'tracker.location': tracks.get_string(1)[0],
                'tracker.size_mb': round(tracks.get_double(3)),
                'duration': tracks.get_integer(4) * 1000,
            })
            album = tracks.get_string(5)[0]
            if album:
                item['album'] = album

            yield item

            count += 1
        log.debug("Got %i results", count)

    def tracks_grouped_by_album(self, filter_artist_name: str=None,
                                filter_album_name: str=None,
                                filter_track_name: str=None) -> calliope.playlist.Playlist:
        '''Return all songs matching specific search criteria.

        These are grouped into their respective releases. Any tracks that
        aren't present on any releases will appear last. Any tracks that
        appear on multiple releases will appear multiple times.

        '''
        if filter_artist_name:
            artist_id = self.artist_id(filter_artist_name)
            artist_select = ""
            artist_pattern = """
                ?track nmm:artist <%s> .
            """ % artist_id
        else:
            artist_select = "nmm:artistName(?artist)"
            artist_pattern = "?track nmm:artist ?artist ."
        if filter_album_name:
            album_pattern = """
                ?album nie:title ?albumTitle .
                FILTER (LCASE(?albumTitle) = "%s")
            """  % _escape(filter_album_name.lower())
        else:
            album_pattern = ""
        if filter_track_name:
            track_pattern = """
                ?track nie:title ?trackTitle .
                FILTER (LCASE(?trackTitle) = "%s")
            """  % _escape(filter_track_name.lower())
        else:
            track_pattern = ""

        query_songs_with_releases = """
        SELECT
            nie:title(?album)
            nie:isStoredAs(?track)
            nie:title(?track)
            nmm:trackNumber(?track)
            %s
        FROM tracker:Audio
        WHERE {
            ?album a nmm:MusicAlbum .
            ?track a nmm:MusicPiece ;
                nmm:musicAlbum ?album .
            %s %s %s
        } ORDER BY
            nie:title(?album)
            nmm:trackNumber(?track)
        """ % (artist_select, artist_pattern, album_pattern, track_pattern)

        songs_with_releases = self.query(query_songs_with_releases)

        if not filter_album_name:
            query_songs_without_releases = """
            SELECT
                nie:isStoredAs(?track)
                ?album
                nie:title(?track)
                %s
            FROM tracker:Audio
            WHERE {
                ?track a nmm:MusicPiece .
                %s %s
                OPTIONAL { ?track nmm:musicAlbum ?album }
                FILTER (! bound (?album))
            } ORDER BY
                %s
                nie:title(?track)
            """ % (artist_select, artist_pattern, track_pattern, artist_select)

            songs_without_releases = self.query(
                query_songs_without_releases)
        else:
            songs_without_releases = None

        while songs_with_releases.next():
            artist_name = filter_artist_name or songs_with_releases.get_string(4)[0]
            album_name = songs_with_releases.get_string(0)[0]
            if songs_with_releases.is_bound(3):
                tracknum = songs_with_releases.get_integer(3)
            else:
                tracknum = None

            item = {
                'album': album_name,
                'creator': artist_name,
                'location': songs_with_releases.get_string(1)[0],
                'title': songs_with_releases.get_string(2)[0],
            }
            if tracknum:
                item['trackNum'] = tracknum
            yield item

        if songs_without_releases:
            while songs_without_releases.next():
                artist_name = filter_artist_name or songs_without_releases.get_string(3)[0]
                yield calliope.playlist.Item({
                    'creator': artist_name,
                    'location': songs_without_releases.get_string(0)[0],
                    'title': songs_without_releases.get_string(2)[0],
                })

    def artists(self) -> calliope.playlist.Playlist:
        '''Return all artists who have at least one track available locally.'''
        query_artists_with_tracks = """
        SELECT
            ?artist_name
        FROM tracker:Audio
        {   ?artist a nmm:Artist ;
            dc:title ?artist_name .
            ?song nmm:artist ?artist
        }
        GROUP BY ?artist ORDER BY ?artist_name
        """
        stmt = self._prepare('artists-with-tracks', query_artists_with_tracks)

        artists_with_tracks = stmt.execute()

        count = 0
        while artists_with_tracks.next():
            log.debug("Got 1 result")
            artist_name = artists_with_tracks.get_string(0)[0]
            yield calliope.playlist.Item({
                'creator': artist_name,
            })
            count += 1
        log.debug("Got %i results", count)

    def search(self, search_text: str) -> calliope.playlist.Playlist:
        '''Return a list of tracks which match 'search_text'.

        The text may be matched in the artist name, track title or album name.
        '''

        search_terms = _escape(search_text)
        query_tracks = """
        SELECT DISTINCT nie:title(?track)
                        nie:isStoredAs(?track)
                        COALESCE(nmm:artistName(?artist), nmm:artistName(?performer), "No artist")
        FROM tracker:Audio
        {
            {
                SELECT ?track nmm:artist(?track) AS ?artist nmm:performer(?track) AS ?performer
                {
                    ?track a nmm:MusicPiece ;
                      fts:match "%s" .
                }
            } UNION {
                SELECT ?track ?artist ?performer
                {
                    ?artist a nmm:Artist ;
                      fts:match "%s" .
                    ?track a nmm:MusicPiece ;
                      nmm:artist ?artist .
                }
            } UNION {
                SELECT ?track ?artist ?performer
                {
                    ?performer a nmm:Artist ;
                      fts:match "%s" .
                    ?track a nmm:MusicPiece ;
                      nmm:performer ?performer .
                }
            } UNION {
                SELECT ?track nmm:artist(?track) AS ?artist nmm:performer(?track) AS ?performer
                {
                    ?album a nmm:MusicAlbum ;
                      fts:match "%s" .
                    ?track a nmm:MusicPiece ;
                      nmm:musicAlbum ?album .
                }
            }
        }
        ORDER BY ?track_title ?artist_name
        """ % (search_terms, search_terms, search_terms, search_terms)

        tracks = self.query(query_tracks)
        while tracks.next():
            yield calliope.playlist.Item({
                'title': tracks.get_string(0)[0],
                'creator': tracks.get_string(2)[0],
                'location': tracks.get_string(1)[0],
                'tracker.location': tracks.get_string(1)[0],
            })


def _resolve_item(tracker: TrackerClient, item: calliope.playlist.Item) -> calliope.playlist.Item:
    item = calliope.playlist.Item(item)
    if 'title' not in item or 'creator' not in item:
        return item.add_warning(
            'tracker', "Cannot set location -- no title or creator info")

    tracker_item = tracker.track(artist_name=item['creator'], track_name=item['title'])

    if tracker_item:
        item.update(tracker_item)
    else:
        item.add_warning('tracker', "Cannot set location -- track not found")

    return item


def annotate_images(tracker: TrackerClient, playlist: calliope.playlist.Playlist) -> calliope.playlist.Playlist:
    """Resolve images from local media-art cache."""
    playlist = list(playlist)
    for item in playlist:
        if 'title' in item and 'creator' in item:
            image_file = MediaArt.get_file(item['creator'], item['title'], 'track')[1]
            if image_file.query_exists():
                item['tracker.track_image'] = image_file.get_uri()
        if 'album' in item and 'creator' in item:
            image_file = MediaArt.get_file(item['creator'], item['album'], 'album')[1]
            if image_file.query_exists():
                item['tracker.album_image'] = image_file.get_uri()
        yield item


def resolve_content(tracker: TrackerClient, playlist: calliope.playlist.Playlist) -> calliope.playlist.Playlist:
    """Resolve content locations from the local filesystem."""
    playlist = list(playlist)
    for item in playlist:
        try:
            item = _resolve_item(tracker, item)
        except RuntimeError as e:
            raise RuntimeError("%s\nItem: %s" % (e, item)) from e

        if 'tracker.location' in item and 'location' not in item:
            item['location'] = item['tracker.location']

        yield item


def resolve_image(tracker: TrackerClient, playlist: calliope.playlist.Playlist) -> calliope.playlist.Playlist:
    """Resolve ``image`` from local media-art cache."""
    playlist = list(playlist)
    for item in playlist:
        if 'image' not in item:
            if 'album' in item and 'creator' in item:
                image_file = MediaArt.get_file(item['creator'], item['album'], 'album')[1]
                if image_file.query_exists():
                    item['image'] = image_file.get_uri()
        if 'image' not in item:
            if 'title' in item and 'creator' in item:
                image_file = MediaArt.get_file(item['creator'], item['title'], 'track')[1]
                if image_file.query_exists():
                    item['image'] = image_file.get_uri()
        yield item


def expand_tracks(tracker: TrackerClient, playlist: calliope.playlist.Playlist) -> calliope.playlist.Playlist:
    """Expand an ``album`` item into a list of the album's tracks."""
    for item in playlist:
        if 'title' in item:
            yield item
        elif 'album' in item:
            yield from tracker.tracks(filter_artist_name=item['creator'],
                                      filter_album_name=item['album'])
        else:
            yield from tracker.tracks(filter_artist_name=item['creator'])
