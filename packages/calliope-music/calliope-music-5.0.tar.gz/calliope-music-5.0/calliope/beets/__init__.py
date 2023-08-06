# Calliope
# Copyright (C) 2020  Sam Thursfield <sam@afuera.me.uk>
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


"""Query the `Beets music organiser <https://beets.io>`_.

See also: :program:`cpe beets` command.

"""

import calliope.playlist

import json
import logging
import pathlib
import shutil
import subprocess
import tempfile

log = logging.getLogger(__name__)


class _BeetsContext():
    def __init__(self):
        self.beet = shutil.which('beet')

    def run_and_stream_output(self, args):
        with tempfile.NamedTemporaryFile(mode='w') as config_override:
            # Output 'length' parameter in seconds, rather than a 'm:ss'
            # string.
            # FIXME: perhaps `beet export` should do this implicitly.
            config_override.write('format_raw_length: yes\n')
            config_override.write('plugins: export\n')
            config_override.flush()

            # We use a larger buffer than the default so things go faster.
            prog = [self.beet, '--config', config_override.name]
            log.info("Running: %s", prog + args)
            with subprocess.Popen(prog + args, stdout=subprocess.PIPE,
                                  bufsize=1 * 1024 * 1024) as proc:
                for line in proc.stdout:
                    yield line


def albums(query: str, include_tracks: bool=False) -> calliope.playlist.Playlist:
    """Export album data from Beets as a playlist.

    Args:
        query: A `Beets query string <https://beets.readthedocs.io/en/stable/reference/query.html>`_ \
               (use ``.`` to return everything).
        include_tracks: Expand the tracklist of each album.

    Returns:
        A playlist containing albums or album tracks.
    """

    beet = _BeetsContext()
    args = ['ls', '--album', '--format=$id', query]
    album_ids = beet.run_and_stream_output(args)

    if include_tracks:
        include_keys = ('artist,album,albumtotal,mb_albumid,mb_artistid,' +
                        'mb_releasegroupid,mb_trackid,path,title,track')
        for album_id in album_ids:
            args = ['export', '--library', '--format', 'jsonlines', '--include-keys',
                    include_keys, 'album_id:%i' % int(album_id)]

            for line in beet.run_and_stream_output(args):
                log.debug("Got line: %s", line)
                item = json.loads(line)
                result = {
                    'album': item['album'],
                    'creator': item['artist'],
                    'title': item['title'],
                    'location': pathlib.Path(item['path']).as_uri(),
                    'trackNum': int(item['track']),
                }
                if item['mb_artistid']:
                    result['musicbrainz.artist_id'] = item['mb_artistid']
                if item['mb_albumid']:
                    result['musicbrainz.release_id'] = item['mb_albumid']
                if item['mb_releasegroupid']:
                    result['musicbrainz.release_group_id'] = item['mb_releasegroupid']
                if item['mb_trackid']:
                    result['musicbrainz.track_id'] = item['mb_trackid']
                yield result
    else:
        include_keys = ('album,albumartist,artist,mb_albumid,mb_albumartistid,' +
                        'mb_releasegroupid,path')
        for album_id in album_ids:
            args = ['export', '--library', '--format', 'jsonlines', '--include-keys',
                    include_keys, 'album_id:%i' % int(album_id)]

            line = next(beet.run_and_stream_output(args))  # pylint: disable=stop-iteration-return
            log.debug("Got line: %s", line)
            album_info = json.loads(line)
            result = {
                'album': album_info['album'],
                'creator': album_info['albumartist'],
                'location': pathlib.Path(album_info['path']).parent.as_uri(),
            }
            if album_info['mb_albumartistid']:
                result['musicbrainz.artist_id'] = album_info['mb_albumartistid']
            if album_info['mb_albumid']:
                result['musicbrainz.release_id'] = album_info['mb_albumid']
            if album_info['mb_releasegroupid']:
                result['musicbrainz.release_group_id'] = album_info['mb_releasegroupid']
            yield result


def artists(query: str) -> calliope.playlist.Playlist:
    """Export artist data from Beets as a playlist.

    Args:
        query: A `Beets query string <https://beets.readthedocs.io/en/stable/reference/query.html>`_ \
            (use ``.`` to return everything).

    Returns:
        A playlist of items with ``creator`` set..
    """

    beet = _BeetsContext()
    args = ['export', '--library', '--format', 'jsonlines', '--include-keys',
            'artist,mb_artistid', query]

    # Beets doesn't have an option to query artists, so we query tracks and
    # then filter the list.
    prev_artist = None
    for line in beet.run_and_stream_output(args):
        log.debug("Got line: %s", line)
        item = json.loads(line)
        if item['artist'] != prev_artist:
            yield {
                'creator': item['artist'],
                'musicbrainz.artist_id': item['mb_artistid'],
            }
            prev_artist = item['artist']


def tracks(query: str) -> calliope.playlist.Playlist:
    """Export songs from Beets as a playlist.

    Args:
        query: A `Beets query string <https://beets.readthedocs.io/en/stable/reference/query.html>`_ \
            (use ``.`` to return everything).

    Returns:
        A playlist.
    """

    beet = _BeetsContext()
    args = ['export', '--library', '--format', 'jsonlines', '--include-keys',
            'artist,title,path,length,mb_artistid,mb_trackid', query]
    for line in beet.run_and_stream_output(args):
        log.debug("Got line: %s", line)
        item = json.loads(line)
        yield {
            'creator': item['artist'],
            'title': item['title'],
            'location': pathlib.Path(item['path']).as_uri(),
            'duration': item['length'] * 1000,
            'musicbrainz.artist_id': item['mb_artistid'],
            'musicbrainz.track_id': item['mb_trackid'],
        }
