# Calliope -- last.fm history
# Copyright (C) 2015,2018-2020  Sam Thursfield <sam@afuera.me.uk>
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


"""Query listening history of a `Last.fm <https://last.fm>`_ user.

The :func:`load` function is the main entry point.

Data is synced locally using the Last.fm `user.getRecentTracks <https://www.last.fm/api/show/user.getRecentTracks>`_
API call. Due to API rate limiting, this is a slow operation for large datasets.

At the time of writing, `Libre.fm <https://libre.fm>`_ also implements this
function and can be queried by setting ``server='libre.fm'``, while
`Listenbrainz <https://listenbrainz.org>`_ does not implement this API.
"""


from datetime import datetime
import logging
import os
import pathlib
import re
import sqlite3
import urllib

import calliope.database
import calliope.lastfm.lastexport
import calliope.sync_operation

log = logging.getLogger(__name__)


_escape_re = re.compile('[^a-zA-Z0-9]')
def escape_for_sql_identifier(name):
    return re.sub(_escape_re, '_', name)


class Store:
    def __init__(self, file_path):
        self.db = sqlite3.connect(file_path)
        self.apply_schema()

    def apply_schema(self):
        self.db.execute(
            'CREATE TABLE IF NOT EXISTS imports_lastfm ('
            '   id INTEGER UNIQUE PRIMARY KEY, '
            '   datetime DATETIME NOT NULL, '
            '   trackname VARCHAR, '
            '   artistname VARCHAR, '
            '   albumname VARCHAR, '
            '   trackmbid VARCHAR, '
            '   artistmbid VARCHAR, '
            '   albummbid VARCHAR '
            ')')
        self.db.execute(
            'CREATE TABLE IF NOT EXISTS import_log ('
            '   page INTEGER UNIQUE'
            ')')

    def commit(self):
        calliope.database.sqlite3_commit_with_retry(self.db, max_retries=3)

    def cursor(self):
        return self.db.cursor()


def escape_for_lastfm_uri(name):
    # I've attempted to use the same rule here as lastfm use for the
    # http://last.fm/music/... URLs. Which appears to be simply the
    # following:
    return name.replace(' ', '+').replace(':', '%2F')


class PageToSync:
    """Represents one page of last.fm history to be synced."""
    def __init__(self, of_number, nf_number):
        self.of_number = of_number
        self.nf_number = nf_number
        self.tracks = None

    def set_tracks(self, tracks):
        self.tracks = tracks


class LastfmSyncOperation(calliope.sync_operation.SyncOperation):
    """Represents a last.fm history sync operation."""
    def __init__(self, lastfm_history, total_pages, total_tracks,
                 newest_tracks, sync_page_callback):
        self.history = lastfm_history
        self.total_tracks = total_tracks
        self.total_pages = total_pages
        self.sync_page_callback = sync_page_callback

        self.newest_tracks = newest_tracks

        self._pages_to_sync = []

    def prepare(self, page_size):
        pages_to_sync = self._query_pages_to_sync(page_size)
        log.debug("Need to sync %i pages", len(pages_to_sync))
        for page_ofnumber in pages_to_sync:
            page = PageToSync(of_number=page_ofnumber,
                              nf_number=(self.total_pages + 1) - page_ofnumber)
            if page_ofnumber == self.total_pages:
                page.set_tracks(self.newest_tracks)
            self._pages_to_sync.append(page)

    def pages(self):
        return self._pages_to_sync

    def process_page(self, page):
        self.sync_page_callback(page)

    def _query_pages_to_sync(self, page_size):
        # Return the list of pages that are *not* recorded as synced in the
        # log.
        #
        # The page numbers returned are oldest-first, so page 1 is the oldest.
        log.debug("Got %i pages of size %i with %i total tracks",
                  self.total_pages, page_size, self.total_tracks)
        sql = """
            WITH RECURSIVE pages(page) AS (SELECT 1 UNION ALL SELECT page + 1 FROM pages LIMIT :totalpages)
                SELECT page FROM pages
                EXCEPT
                SELECT page FROM import_log;
            """

        cursor = self.history.store.cursor()
        log.debug("Executing: %s", sql)
        cursor.execute(sql, { 'totalpages': self.total_pages, })
        return [row[0] for row in cursor.fetchall()]


class ListenHistory:
    def __init__(self, store, username, server, retry_on_error):
        """Database of listening history for a given user.

        This should be created using the :func:`load` function.

        You will probably first want to sync the data. As this is a slow
        operation, it is implemented as a generator so you can give feedback on
        the sync operation's progress. Here's a simple example::

            op = lastfm_history.prepare_sync()
            for i, page in enumerate(op.pages_to_sync):
                print(f"Syncing page {i}")
                lastfm_history.sync_page(page)
        """
        self.store = store
        self.username = username
        self.server = server
        self.retry_on_error = retry_on_error

    def prepare_sync(self):
        """Queries last.fm for updates and returns a SyncOperation object."""

        log.debug("Fetching newest page of scrobbles")
        total_pages, total_tracks, tracks = self._fetch_page(nf_page=1)
        page_size = len(tracks)

        op = LastfmSyncOperation(
            self, total_pages, total_tracks, tracks, self._sync_page
        )
        op.prepare(page_size)
        return op

    def _fetch_page(self, nf_page):
        """Queries one page of scrobbles from the last.fm server.

        The pages are counted with newest first in the last.fm API. So page
        1 is the newest page of scrobbles.

        Returns a tuple of (total_pages, total_tracks, tracks).

        """
        while True:
            try:
                gen = calliope.lastfm.lastexport.get_tracks(
                    self.server, self.username, startpage=nf_page,
                    tracktype='recenttracks', retry_on_error=self.retry_on_error)
                page, _total_pages, _total_tracks, tracks = next(gen)
                assert page == nf_page
            except urllib.error.URLError as e:
                raise RuntimeError("Unable to sync lastfm history due to network "
                                "error: {}".format(e)) from e

            if tracks is None:
                # This can happen when a fetch request times out.
                # The 'lastexport' will eventually raise an exception
                # after retrying a few times.
                continue
            break
        return _total_pages, _total_tracks, tracks

    def _sync_page(self, page):
        if not page.tracks:
            _, _, page.tracks = self._fetch_page(page.nf_number)
        for scrobble in page.tracks:
            self._intern_scrobble(scrobble)
        if page.nf_number > 1:
            cursor = self.store.cursor()
            cursor.execute('INSERT OR IGNORE INTO import_log (page) VALUES (:page_of_number)',
                           { 'page_of_number': page.of_number })
        self.store.commit()

    def _intern_scrobble(self, play_info):
        datetime, trackname, artistname, albumname, trackmbid, artistmbid, \
            albummbid = play_info

        cursor = self.store.cursor()
        find_lastfm_sql = 'SELECT id FROM imports_lastfm ' \
                          '  WHERE datetime = ? AND trackname = ? AND artistname = ?'
        row = cursor.execute(find_lastfm_sql, [datetime, trackname, artistname]).fetchone()
        if row is None:
            cursor.execute(
                'INSERT INTO imports_lastfm(datetime, trackname, '
                ' artistname, albumname, trackmbid, artistmbid, '
                ' albummbid) VALUES (?, ?, ?, ?, ?, ?, ?)',
                [datetime, trackname, artistname, albumname, trackmbid,
                 artistmbid, albummbid])
            scrobble_id = cursor.lastrowid
        else:
            scrobble_id = row[0]
        return scrobble_id

    def annotate(self, item):
        if 'creator' in item:
            sql = 'SELECT COUNT(id) FROM imports_lastfm WHERE artistname == ?;'
            cursor = self.store.cursor()
            cursor.execute(sql, (item['creator'],))
            row = cursor.fetchone()
            item['lastfm.artist_playcount'] = int(row[0])

            if 'title' in item:
                sql = ('SELECT COUNT(id) FROM imports_lastfm ' +
                       'WHERE artistname == ? AND trackname == ?;')
                cursor = self.store.cursor()
                cursor.execute(sql, (item['creator'], item['title'],))
                row = cursor.fetchone()
                item['lastfm.playcount'] = int(row[0])
        return item

    def scrobbles(self):
        return self.listens()

    def listens(self):
        '''Return individual scrobbles as a Calliope playlist.'''
        sql = 'SELECT datetime, trackname, artistname, albumname, ' + \
              ' trackmbid, artistmbid, albummbid FROM imports_lastfm ' + \
              ' ORDER BY datetime DESC'
        cursor = self.store.cursor()
        cursor.execute(sql)
        for row in cursor:
            datetime, trackname, artistname, albumname, trackmbid, \
                artistmbid, albummbid = row
            item = {
                'creator': artistname,
                'album': albumname,
                'title': trackname,
                'lastfm.scrobble_datetime': datetime
            }
            if artistmbid:
                item['musicbrainz.artist_id'] = artistmbid
            if albummbid:
                item['musicbrainz.album_id'] = albummbid
            if trackmbid:
                item['musicbrainz.identifier'] = trackmbid
            yield item

    def artists(self, first_play_before=None, first_play_since=None,
                last_play_before=None, last_play_since=None, min_listens=1,
                show_listens_since=None):
        '''Return artists from the lastfm history.

        The following keyword arguments can be used to filter the returned
        results.

          * first_play_before: only artists who were played before the given date
          * first_play_since: only artists who were never played before the given date
          * last_play_before: only artists who were never played after the given date
          * last_play_since: only artists who were last played after the given date
          * min_listens: only artists who have N or more listens.

        The following keyword arguments query extra information:

          * show_listens_since: number of listens since a given date

        '''

        sql_template = '''
              WITH
                  all_listens AS (
                      SELECT artistname, artistmbid, datetime AS l_timestamp, DATETIME(datetime, 'unixepoch') as l_datetime
                        FROM imports_lastfm
                  ),
                  listens AS (
                      SELECT artistname, artistmbid, COUNT(artistname) AS listencount, MIN(l_timestamp) AS firstplay, MAX(l_timestamp) AS lastplay
                        FROM all_listens
                       GROUP BY artistname
                       {having_clause}
                  ),
                  listens_since AS (
                      SELECT DISTINCT artistname, COUNT(artistname) AS listencount
                        FROM all_listens
                       WHERE l_datetime >= DATETIME(?)
                       GROUP BY artistname
                  )
              SELECT listens.listencount, listens.artistname, listens.artistmbid, listens.firstplay, listens.lastplay,
                     listens_since.listencount
                FROM listens INNER JOIN listens_since ON listens.artistname == listens_since.artistname
                     {order_clause}
              '''

        having_clause = ""
        order_clause = ""

        sql_filters = []
        if min_listens > 1:
            sql_filters.append('listencount >= {}'.format(min_listens))
        if first_play_before:
            sql_filters.append('firstplay < {}'.format(first_play_before.timestamp()))
        if first_play_since:
            sql_filters.append('firstplay >= {}'.format(first_play_since.timestamp()))
        if last_play_before:
            sql_filters.append('lastplay < {}'.format(last_play_before.timestamp()))
        if last_play_since:
            sql_filters.append('lastplay >= {}'.format(last_play_since.timestamp()))

        if sql_filters:
            having_clause = ' HAVING ' + ' AND '.join(sql_filters)

        order_clause = 'ORDER BY listens.artistname'

        sql = sql_template.format(having_clause=having_clause, order_clause=order_clause)
        log.debug("sql: %s", sql)

        cursor = self.store.cursor()
        cursor.execute(sql, (show_listens_since or 0, ))
        for row in cursor:
            playcount, artistname, artistmbid, first_play, last_play, listens_since = row
            item = {
                'creator': artistname,
                'lastfm.playcount': playcount,
                'lastfm.first_play': datetime.fromtimestamp(first_play).isoformat(),
                'lastfm.last_play': datetime.fromtimestamp(last_play).isoformat(),
            }
            if artistmbid:
                item['musicbrainz.artist'] = artistmbid
            if show_listens_since:
                item['lastfm.listens_since_%s' % show_listens_since.strftime('%Y_%m_%d')] = listens_since
            yield item

    def tracks(self, first_play_before=None, first_play_since=None,
               last_play_before=None, last_play_since=None, min_listens=1,
               show_listens_since=None):
        '''Return tracks from the lastfm history.

        The following keyword arguments can be used to filter the returned
        results.

          * first_play_before: only tracks which were played before the given date
          * first_play_since: only tracks which were never played before the given date
          * last_play_before: only tracks which were never played after the given date
          * last_play_since: only tracks which were last played after the given date
          * min_listens: only tracks which have N or more listens.

        The following keyword arguments query extra information:

          * show_listens_since: number of listens since a given date
        '''

        # last.fm doesn't give us a single unique identifier for the tracks, so
        # we construct a trackid by concatenating the two fields that are
        # guaranteed to be present for every track (which are 'artistname' and
        # 'trackname').

        sql_template = '''
              WITH
                  all_listens AS (
                      SELECT (artistname || \',\' || trackname) AS trackid, trackname, artistname, albumname,
                             artistmbid, trackmbid, albummbid, datetime AS l_timestamp,
                             DATETIME(datetime, 'unixepoch') as l_datetime
                        FROM imports_lastfm
                  ),
                  listens AS (
                      SELECT trackid, trackname, artistname, albumname, artistmbid, trackmbid, albummbid,
                             COUNT(trackid) AS listencount, MIN(l_timestamp) AS firstplay, MAX(l_timestamp) AS lastplay
                        FROM all_listens
                       GROUP BY trackid
                       {having_clause}
                  ),
                  listens_since AS (
                      SELECT DISTINCT trackid, COUNT(trackid) AS listencount
                        FROM all_listens
                       WHERE l_datetime >= DATETIME(?)
                       GROUP BY trackid
                  )
              SELECT listens.listencount, listens.trackname, listens.artistname, listens.albumname,
                     listens.trackmbid, listens.artistmbid, listens.albummbid,
                     listens.firstplay, listens.lastplay, listens_since.listencount
                FROM listens INNER JOIN listens_since ON listens.trackid == listens_since.trackid
                     {order_clause}
              '''

        having_clause = ""
        order_clause = ""

        sql_filters = []
        if min_listens > 1:
            sql_filters.append('listencount >= {}'.format(min_listens))
        if first_play_before:
            sql_filters.append('firstplay < {}'.format(first_play_before.timestamp()))
        if first_play_since:
            sql_filters.append('firstplay >= {}'.format(first_play_since.timestamp()))
        if last_play_before:
            sql_filters.append('lastplay < {}'.format(last_play_before.timestamp()))
        if last_play_since:
            sql_filters.append('lastplay >= {}'.format(last_play_since.timestamp()))

        if sql_filters:
            having_clause = ' HAVING ' + ' AND '.join(sql_filters)

        order_clause = 'ORDER BY listens.trackid'

        sql = sql_template.format(having_clause=having_clause, order_clause=order_clause)
        log.debug("SQL: %s, Show listens since: %s", sql, show_listens_since)

        cursor = self.store.cursor()
        cursor.execute(sql, (show_listens_since or 0, ))
        for row in cursor:
            playcount, trackname, artistname, albumname, trackmbid, \
                artistmbid, albummbid, first_play, last_play, listens_since = row
            item = {
                'creator': artistname,
                'album': albumname,
                'title': trackname,
                'lastfm.playcount': playcount,
                'lastfm.first_play': datetime.fromtimestamp(first_play).isoformat(),
                'lastfm.last_play': datetime.fromtimestamp(last_play).isoformat(),
            }
            if artistmbid:
                item['musicbrainz.artist_id'] = artistmbid
            if albummbid:
                item['musicbrainz.album_id'] = albummbid
            if trackmbid:
                item['musicbrainz.identifier'] = trackmbid
            if show_listens_since:
                item['lastfm.listens_since_%s' % show_listens_since.strftime('%Y_%m_%d')] = listens_since
            yield item


def load(username: str, server: str='last.fm', retry_on_error: bool=True,
         cachedir: pathlib.Path=None) -> ListenHistory:
    """Load the listen history database for `user`."""

    if cachedir is None:
        cachedir = calliope.cache.save_cache_path('calliope')

    namespace = 'lastfm-history.%s' % username

    store_path = os.path.join(cachedir, namespace) + '.sqlite'
    store = Store(store_path)

    history = ListenHistory(store, username, server, retry_on_error)
    return history
