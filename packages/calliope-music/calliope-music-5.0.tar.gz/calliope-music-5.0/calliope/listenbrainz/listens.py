# Calliope -- Listenbrainz listen history
# Copyright (C) 2021 Sam Thursfield <sam@afuera.me.uk>
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


"""Query listening history of a `Listenbrainz <listenbrainz.org/>`_ user.

The :func:`load` function is the main entry point.

Data is synced locally using the Listenbrainz
`listens <https://listenbrainz.readthedocs.io/en/production/dev/api/#get--1-user-(user_name)-listens>`_
API call.
"""

import requests

from datetime import datetime
import collections
import dataclasses
import logging
import os
import pathlib
import sqlite3

import calliope.cache
import calliope.database
import calliope.subprojects.pylistenbrainz as pylistenbrainz
import calliope.sync_operation
from . import api

log = logging.getLogger(__name__)


class Store:
    def __init__(self, file_path):
        self.db = sqlite3.connect(file_path)
        self.apply_schema()

    def apply_schema(self):
        # MBID (MusicBrainz ID) is canonical identifier for a song/artist.
        # It is sometimes available and sometimes not.
        # MSID (MessyBrainz ID) is an identifier based on the track tags.
        # A song might have several MSIDs, however, it is guaranteed to be set.
        # See also:
        # https://blog.metabrainz.org/2018/08/12/gsoc-2018-a-way-to-associate-listens-with-mbids/
        self.db.execute(
            'CREATE TABLE IF NOT EXISTS imports_listenbrainz ('
            '   id INTEGER UNIQUE PRIMARY KEY, '
            '   listened_at DATETIME NOT NULL, '
            '   artist_msid VARCHAR, '
            '   recording_msid VARCHAR, '
            '   release_msid VARCHAR, '
            '   track_name VARCHAR, '
            '   artist_name VARCHAR, '
            '   release_name VARCHAR, '
            '   tracknumber INTEGER,'
            '   recording_mbid VARCHAR, '
            '   artist_mbids VARCHAR, '
            '   release_mbid VARCHAR, '
            '   release_group_mbid VARCHAR, '
            '   work_mbids VARCHAR, '
            '   origin_url VARCHAR'
            ')')

    def commit(self):
        calliope.database.sqlite3_commit_with_retry(self.db, max_retries=3)

    def cursor(self):
        return self.db.cursor()


@dataclasses.dataclass
class PageToSync:
    """Represents one page of Listenbrainz history to be synced.

    Pages are delimited by the 'max_ts' timestamp. The page will contain
    listens with timestamp < max_ts.
    """
    size: int
    number: int
    max_ts: int = None
    min_ts: int = None
    listens: [pylistenbrainz.Listen] = None

    def set_listens(self, listens):
        self.listens = listens

    def set_max_timestamp(self, max_ts):
        self.max_ts = max_ts

    def set_min_timestamp(self, min_ts):
        self.min_ts = min_ts


class SyncOperation(calliope.sync_operation.SyncOperation):
    """Represents a Listenbrainz history sync operation."

    We process remote listens from newest to oldest, using the `max_ts`
    parameter to control paging. As of January 2022 this is the only
    method that the Listenbrainz API makes possible.

    We assume that remote listens are never deleted or modified. This is untrue
    but makes the sync more efficent. If existing remote listens have changed,
    delete the local cache completely to cause a full resync.

    The initial sync may be interrupted so we handle two possibilities
    each time we sync:

      * there are remote listens newer than everything in our cache.
      * there are remote listens older than everything in our cache.

    """

    def __init__(self, history, client: pylistenbrainz.ListenBrainz):
        self._history = history
        self._client = client

        self._pages_to_sync = []
        self._to_cache = None
        self._max_local_timestamp = None
        self._min_local_timestamp = None
        self._previous_page = None

    def prepare(self, page_size) -> [PageToSync]:
        """Check stored data against remote."""

        remote_listen_count = self._get_listen_count()
        local_listen_count, max_local_timestamp, min_local_timestamp = self._query_cache()
        log.debug("Cached: %i/%i listens", local_listen_count, remote_listen_count)

        to_cache = remote_listen_count - local_listen_count
        if to_cache <= 0:
            log.debug("Nothing to sync.")
            if to_cache < 0:
                log.warning(
                    "More listens cached than available in Listenbrainz. "
                    "Deleted data in Listenbrainz will remain cached "
                    "unless you delete the local cache and sync again."
                )
            self._to_cache = 0
            self._pages_to_sync = []
            return

        newest_listens = self._get_listens(count=page_size)
        max_remote_timestamp = newest_listens[0].listened_at

        pages_to_sync = list(self._make_pages(page_size, to_cache))
        log.debug("Newest remote listen: %i, newest cached listen: %i",
                  max_remote_timestamp, max_local_timestamp)
        if max_remote_timestamp > max_local_timestamp:
            pages_to_sync[0].set_listens(newest_listens)
            pages_to_sync[0].set_max_timestamp(max_remote_timestamp)
            pages_to_sync[0].set_min_timestamp(newest_listens[-1].listened_at)

        self._to_cache = to_cache
        self._max_local_timestamp = max_local_timestamp
        self._min_local_timestamp = min_local_timestamp
        self._pages_to_sync = pages_to_sync

    def _store_listens(self, listens):
        new_count = 0
        for listen in listens:
            _, new = self._history.intern_listen(listen)
            if new:
                new_count += 1
        self._history.store.commit()
        return new_count

    def process_page(self, page):
        if self._to_cache <= 0:
            log.debug("Nothing more to pull, skipping page.")
            return

        if self._previous_page:
            page.set_max_timestamp(self._previous_page.min_ts)
            log.debug("Setting max ts from prev page %s %i", self._previous_page, self._previous_page.min_ts)

        log.debug("Sync page %i/%i: max_ts: %s, size: %i", page.number,
                  len(self._pages_to_sync), page.max_ts, page.size)

        listens = page.listens or self._get_listens(
            count=page.size,
            max_ts=page.max_ts,
        )

        if listens:
            min_timestamp = listens[-1].listened_at
            log.debug("Lowest timestamp on this page: %i; max cached: %i",
                      min_timestamp, self._max_local_timestamp)

            if min_timestamp < self._max_local_timestamp:
                log.debug("Last page of new listens was pulled. Jumping on to "
                          "before oldest cached listen.")
                min_timestamp = self._min_local_timestamp
                first_old_listens = self._get_listens(
                    count=page.size, max_ts=min_timestamp
                )
                if len(first_old_listens) == 0:
                    log.debug("No more listens to pull; listen count may be wrong")
                listens += first_old_listens
                self._max_local_timestamp = 0

            new_count = self._store_listens(listens)
            page.set_min_timestamp(min_timestamp)
            self._previous_page = page

            self._to_cache -= len(listens)
            log.debug("New listens: %i. Listens still to cache: %s", new_count,
                      self._to_cache)

            while self._to_cache <= 0 and len(listens) == page.size:
                # Sometimes ListenBrainz underestimates listen count. Keep
                # pulling until we actually run out of data.
                #
                # https://tickets.metabrainz.org/browse/LB-763
                max_ts = listens[-1].listened_at
                listens = self._get_listens(
                    count=page.size, max_ts=max_ts,
                )
                log.debug("Got extra %i listens with max_ts %i", len(listens), max_ts)
                new_count = self._store_listens(listens)
                log.debug("Stored %i new listens.", new_count)
        else:
            log.warning("No listens returned. Sync ends.")
            self._to_cache = 0

    def pages(self):
        return self._pages_to_sync

    def _get_listen_count(self):
        """Queries total # of listens in Listenbrainz server."""
        return self._client.get_user_listen_count(self._history.username)

    def _get_listens(self, count=None, max_ts=None):
        """Queries one page of listens from the Listenbrainz server."""
        return self._client.get_listens(self._history.username, count=count, max_ts=max_ts)

    def _make_pages(self, page_size, listen_count):
        page_number = 0
        while page_number * page_size < listen_count:
            page = PageToSync(page_size, page_number)
            page_number += 1
            yield page

    def _query_cache(self):
        sql = "SELECT COUNT(id), MAX(listened_at), MIN(listened_at) FROM imports_listenbrainz"

        cursor = self._history.store.cursor()
        log.debug("Executing: %s", sql)
        cursor.execute(sql)
        rows = cursor.fetchall()

        listen_count = int(rows[0][0])
        max_timestamp = int(rows[0][1] or 0)
        min_timestamp = int(rows[0][2] or 0)
        log.debug("Cache info: %s total listens, max timestamp %s, min timestamp %s",
                  listen_count, max_timestamp, min_timestamp)
        return listen_count, max_timestamp, min_timestamp


def maybe_set(item, key, value):
    if value:
        item[key] = value


HistogramEntry = collections.namedtuple('HistogramEntry', ['bucket', 'count'])


class History:
    def __init__(self, store, username):
        """Database of listening history for a given user.

        This should be created using the :func:`load` function.

        You will probably first want to sync the data. As this is a slow
        operation, it is implemented as a generator so you can give feedback on
        the sync operation's progress. Here's a simple example::

            op = listen_history.prepare_sync()
            for i, page in enumerate(op.pages_to_sync):
                print(f"Syncing page {i}")
                listen_history.sync_page(page)
        """
        self.store = store
        self.username = username

    def prepare_sync(self, page_size=None):
        """Query ListenBrainz for updates and returns a SyncOperation object."""

        # We set this here so tests can override the max value.
        page_size = page_size or api.MAX_ITEMS_PER_GET

        client = pylistenbrainz.ListenBrainz()

        op = SyncOperation(self, client)
        try:
            op.prepare(page_size)
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Could not connect to remote server.\n\n"
                               f"{e}") from e
        return op

    def intern_listen(self, listen):
        cursor = self.store.cursor()
        find_listen_sql = 'SELECT id FROM imports_listenbrainz ' \
                          '  WHERE listened_at = ? AND recording_msid = ?'
        row = cursor.execute(find_listen_sql, [
            listen.listened_at, listen.additional_info['recording_msid']
        ]).fetchone()
        if row is None:
            cursor.execute(
                'INSERT INTO imports_listenbrainz('
                '  listened_at, '
                '  recording_msid, '
                '  artist_msid, '
                '  release_msid, '
                '  track_name, '
                '  artist_name, '
                '  release_name, '
                '  tracknumber, '
                '  recording_mbid, '
                '  artist_mbids, '
                '  release_mbid, '
                '  release_group_mbid, '
                '  work_mbids, '
                '  origin_url'
                ') VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                [
                    listen.listened_at,
                    listen.additional_info['recording_msid'],
                    listen.additional_info['artist_msid'],
                    listen.additional_info['release_msid'],
                    listen.track_name,
                    listen.artist_name,
                    listen.release_name,
                    listen.tracknumber,
                    listen.recording_mbid or None,
                    ','.join(listen.artist_mbids) or None,
                    listen.release_mbid or None,
                    listen.release_group_mbid or None,
                    ','.join(listen.work_mbids) or None,
                    listen.additional_info.get('origin_url') or None,
                ])
            listen_id = cursor.lastrowid
            new = True
        else:
            listen_id = row[0]
            new = False
        return (listen_id, new)

    def annotate(self, item):
        if 'creator' in item:
            sql = 'SELECT COUNT(id) FROM imports_listenbrainz WHERE artist_name == ?;'
            cursor = self.store.cursor()
            cursor.execute(sql, (item['creator'],))
            row = cursor.fetchone()
            item['listenbrainz.artist_playcount'] = int(row[0])

            if 'title' in item:
                sql = ('SELECT COUNT(id) FROM imports_listenbrainz ' +
                       'WHERE artist_name == ? AND track_name == ?;')
                cursor = self.store.cursor()
                cursor.execute(sql, (item['creator'], item['title'],))
                row = cursor.fetchone()
                item['listenbrainz.playcount'] = int(row[0])
        return item

    def listens(self):
        '''Return individual listens as a Calliope playlist.'''
        sql = ('SELECT ' +
               '  listened_at, ' +
               '  recording_msid, ' +
               '  artist_msid, ' +
               '  release_msid, ' +
               '  track_name, ' +
               '  artist_name, ' +
               '  release_name, ' +
               '  tracknumber, ' +
               '  recording_mbid, ' +
               '  artist_mbids, ' +
               '  release_mbid, ' +
               '  release_group_mbid, ' +
               '  work_mbids, ' +
               '  origin_url ' +
               ' FROM imports_listenbrainz ' +
               ' ORDER BY listened_at DESC')
        cursor = self.store.cursor()
        cursor.execute(sql)
        for row in cursor:
            (
                listened_at,
                recording_msid,
                artist_msid,
                release_msid,
                track_name,
                artist_name,
                release_name,
                tracknumber,
                recording_mbid,
                artist_mbids,
                release_mbid,
                release_group_mbid,
                work_mbids,
                origin_url,
            ) = row
            item = {
                'listenbrainz.listened_at': listened_at,
                'listenbrainz.recording_msid': recording_msid,
                'listenbrainz.artist_msid': artist_msid,
                'listenbrainz.release_msid': release_msid,
                'creator': artist_name,
                'title': track_name,
            }
            maybe_set(item, 'album', release_name)
            maybe_set(item, 'trackNum', tracknumber)
            maybe_set(item, 'musicbrainz.artist_ids', artist_mbids)
            maybe_set(item, 'musicbrainz.recording_mbid', recording_mbid)
            maybe_set(item, 'musicbrainz.release_id', release_mbid)
            maybe_set(item, 'musicbrainz.release_group_id', release_group_mbid)
            maybe_set(item, 'musicbrainz.work_mbid', work_mbids)
            maybe_set(item, 'listenbrainz.origin_url', origin_url)
            yield item

    def artists(self, first_play_before=None, first_play_since=None,
                last_play_before=None, last_play_since=None, min_listens=1,
                show_listens_since=None):
        '''Return artists from the Listenbrainz history.

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
                      SELECT
                             artist_msid,
                             artist_name,
                             artist_mbids,
                             listened_at AS l_timestamp,
                             DATETIME(listened_at, 'unixepoch') as l_datetime
                        FROM imports_listenbrainz
                  ),
                  listens AS (
                      SELECT
                             artist_msid,
                             artist_name,
                             artist_mbids,
                             COUNT(artist_name) AS listencount,
                             MIN(l_timestamp) AS firstplay,
                             MAX(l_timestamp) AS lastplay
                        FROM all_listens
                       GROUP BY artist_msid
                       {having_clause}
                  ),
                  listens_since AS (
                      SELECT DISTINCT
                             artist_msid,
                             artist_name,
                             COUNT(artist_msid) AS listencount
                        FROM all_listens
                       WHERE l_datetime >= DATETIME(?)
                       GROUP BY artist_msid
                  )
              SELECT listens.listencount,
                     listens.artist_msid,
                     listens.artist_name,
                     listens.artist_mbids,
                     listens.firstplay,
                     listens.lastplay,
                     listens_since.listencount
                FROM listens INNER JOIN listens_since ON listens.artist_msid == listens_since.artist_msid
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

        if show_listens_since:
            log.debug("Showing listens since: %s", show_listens_since)

        order_clause = 'ORDER BY listens.artist_name'

        sql = sql_template.format(having_clause=having_clause, order_clause=order_clause)
        log.debug("sql: %s", sql)

        cursor = self.store.cursor()
        cursor.execute(sql, (show_listens_since or 0, ))
        for row in cursor:
            (
                playcount,
                artist_msid,
                artist_name,
                artist_mbids,
                first_play,
                last_play,
                listens_since
            ) = row
            item = {
                'creator': artist_name,
                'listenbrainz.artist_msid': artist_msid,
                'listenbrainz.playcount': playcount,
                'listenbrainz.first_play': datetime.fromtimestamp(first_play).isoformat(),
                'listenbrainz.last_play': datetime.fromtimestamp(last_play).isoformat(),
            }
            maybe_set(item, 'musicbrainz.artist', artist_mbids)
            if show_listens_since:
                item['listenbrainz.listens_since_%s' % show_listens_since.strftime('%Y_%m_%d')] = listens_since
            yield item

    def tracks(self, first_play_before=None, first_play_since=None,
               last_play_before=None, last_play_since=None, min_listens=1,
               show_listens_since=None):
        '''Return tracks from the listenbrainz history.

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

        # Using recording_msid as unique identifier for tracks, we group
        # listens per-track and calculate some extra timestamp info for them.
        sql_template = '''
              WITH
                  track_listens_with_times AS (
                      SELECT COUNT(recording_msid) AS listencount,
                             MIN(listened_at) AS firstplay,
                             MAX(listened_at) AS lastplay,
                             DATETIME(listened_at, 'unixepoch') as l_datetime,
                             *
                        FROM imports_listenbrainz
                       GROUP BY recording_msid
                       {having_clause}
                  )
              SELECT
                     listencount,
                     firstplay,
                     lastplay,
                     recording_msid,
                     artist_msid,
                     release_msid,
                     track_name,
                     artist_name,
                     release_name,
                     recording_mbid,
                     artist_mbids,
                     release_mbid,
                     release_group_mbid,
                     work_mbids
                FROM track_listens_with_times
                WHERE l_datetime >= DATETIME(?)
                GROUP BY recording_msid
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

        order_clause = 'ORDER BY l_datetime'

        sql = sql_template.format(having_clause=having_clause, order_clause=order_clause)
        log.debug("SQL: %s, Show listens since: %s", sql, show_listens_since)

        cursor = self.store.cursor()
        cursor.execute(sql, (show_listens_since or 0, ))
        for row in cursor:
            (
                listencount,
                firstplay,
                lastplay,
                recording_msid,
                artist_msid,
                release_msid,
                track_name,
                artist_name,
                release_name,
                recording_mbid,
                artist_mbids,
                release_mbid,
                release_group_mbid,
                work_mbids,
            ) = row
            item = {
                'creator': artist_name,
                'album': release_name,
                'title': track_name,
                'listenbrainz.playcount': listencount,
                'listenbrainz.first_play': datetime.fromtimestamp(firstplay).isoformat(),
                'listenbrainz.last_play': datetime.fromtimestamp(lastplay).isoformat(),
                'listenbrainz.recording_msid': recording_msid,
                'listenbrainz.artist_msid': artist_msid,
                'listenbrainz.release_msid': release_msid,
            }
            if recording_mbid:
                item['musicbrainz.recording'] = recording_mbid
            if artist_mbids:
                item['musicbrainz.artist'] = artist_mbids
            if release_mbid:
                item['musicbrainz.release'] = release_mbid
            if release_group_mbid:
                item['musicbrainz.release_group'] = release_group_mbid
            if work_mbids:
                item['musicbrainz.work'] = work_mbids
            yield item

    def histogram(self, bucket='year'):
        """Listen counts grouped per day/week/month/year."""

        assert bucket in ['day', 'week', 'month', 'year']

        sql = '''
            SELECT DATETIME(listened_at, 'unixepoch', ?) as bucket, COUNT(id)
              FROM imports_listenbrainz
             GROUP BY bucket;
        '''
        if bucket == 'day':
            modifier = 'start of day'
        elif bucket == 'week':
            modifier = 'weekday 0'
        elif bucket == 'month':
            modifier = 'start of month'
        elif bucket == 'year':
            modifier = 'start of year'

        cursor = self.store.cursor()
        cursor.execute(sql, (modifier, ))

        histogram = []

        for row in cursor:
            entry = HistogramEntry(
                bucket=row[0],
                count=row[1],
            )
            histogram.append(entry)

        return histogram


def load(username: str, cachedir: pathlib.Path = None) -> History:
    """Load the listen history database for `user`."""

    if cachedir is None:
        cachedir = calliope.cache.save_cache_path('calliope')

    namespace = 'listenbrainz-history.%s' % username

    store_path = os.path.join(cachedir, namespace) + '.sqlite'
    store = Store(store_path)

    history = History(store, username)
    return history
