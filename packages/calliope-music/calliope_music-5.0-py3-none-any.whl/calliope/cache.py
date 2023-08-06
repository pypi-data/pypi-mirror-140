# Calliope
# Copyright (C) 2018-2019  Sam Thursfield <sam@afuera.me.uk>
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


import json
import logging
import os
import pathlib
import sqlite3

import calliope.database

log = logging.getLogger(__name__)

'''cache: Simple key-value store for use by Calliope tools.

Many Calliope tools contact online services. We should always cache the
responses we get to avoid repeating the same request. This module provides a
simple key/value store interface that should be used for caching.

Use the `open()` module method to access a cache.

Multiple processes can read and write to a cache concurrently and can share data
appropriately.

'''


# Copied from pyxdg under the LGPL2 license. We avoid using the
# xdg.BaseDirectories module directly because we want to avoid using a globally
# cached xdg_cache_home directory, so we can run tests with
# click.testing.CliRunner and override XDG_CACHE_HOME in the environment.
def save_cache_path(*resource):
    """Ensure ``$XDG_CACHE_HOME/<resource>/`` exists, and return its path.
    'resource' should normally be the name of your application or a shared
    resource."""
    _home = os.path.expanduser('~')
    xdg_cache_home = os.environ.get('XDG_CACHE_HOME') or \
                os.path.join(_home, '.cache')

    resource = os.path.join(*resource)
    assert not resource.startswith('/')
    path = os.path.join(xdg_cache_home, resource)
    if not os.path.isdir(path):
        os.makedirs(path)
    return pathlib.Path(path)


class Cache():
    '''Abstract base class that defines the Cache interface.

    Do not use this class directly. Call the `open()` module method instead.

    '''
    def __init__(self, namespace, cachedir=None):
        raise NotImplementedError("Use the cache.open() function to open a cache")

    def lookup(self, key):
        '''Lookup 'key' in the cache.

        Returns a tuple of (found, value).

        '''
        raise NotImplementedError()

    def store(self, key, value):
        '''Store 'value' in the cache under the given key.

        The contents of 'value' must be representable as JSON data.

        '''
        raise NotImplementedError()

    def wrap(self, key, call):
        '''Either run call() and save the result, or return cached result.

        This is intended for use when calling remote APIs. Lots of network access
        can be avoided if the result is saved for future use. For example, this
        snipped is used in the lastfm.similar_artists() function:

            def similar_artists(lastfm, artist_name):
                entry = lastfm.cache.wrap('artist-similar:{}'.format(artist_name),
                    lambda: lastfm.api.artist.get_similar(artist_name, limit=count))

        We currently have no mechanism for 'cache expiry'.

        '''
        found, entry = self.lookup(key)
        if found:
            log.debug("Found {} in cache".format(key))
        else:
            log.debug("Didn't find {} in cache, running remote query".format(key))
            entry = call()
            self.store(key, entry)
        return entry


class SqliteCache(Cache):
    '''Cache implemention which uses the SQLite database library.'''

    # FIXME: this would be much faster if we could use sqlite3_stmt_prepare.
    # Seems that the sqlite3 module doesn't expose that though.

    def __init__(self, namespace, cachedir=None):  # pylint: disable=super-init-not-called
        if cachedir is None:
            cachedir = save_cache_path('calliope')

        self._path = os.path.join(cachedir, namespace) + '.sqlite'
        self.__connection = None

    def _connection(self):
        if self.__connection:
            return self.__connection

        self.__connection = sqlite3.connect(self._path)
        # See: https://sqlite.org/wal.html
        self.__connection.execute('PRAGMA journal_mode=WAL;')
        self.__connection.execute('CREATE TABLE IF NOT EXISTS cache (key STRING UNIQUE, value);')
        return self.__connection

    def lookup(self, key):
        '''Lookup 'key' in the cache.

        Returns a tuple of (found, value).

        '''
        if not os.path.exists(self._path):
            return False, None
        db = self._connection()
        cursor = db.execute('SELECT value FROM cache WHERE key=?', (key,))
        row = cursor.fetchone()
        if row:
            return (True, json.loads(row[0]))
        else:
            return (False, None)

    def store(self, key, value):
        db = self._connection()
        db.execute('INSERT OR REPLACE INTO cache (key, value) VALUES (?, ?);',
                   (key, json.dumps(value)))
        calliope.database.sqlite3_commit_with_retry(db, max_retries=3)


def open(namespace, cachedir=None):  # pylint: disable=redefined-builtin
    '''Open a cache using the best available cache implementation.

    The 'namespace' parameter should usually correspond with the name of tool
    or module using the cache.

    The 'cachedir' parameter is mainly for use during automated tests.

    '''
    return SqliteCache(namespace, cachedir=cachedir)
