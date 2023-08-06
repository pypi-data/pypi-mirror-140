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


"""Copy music content between locations.

See also: the :command:`cpe sync` command.

"""


import itertools
import logging
import os
import pathlib
import string
import subprocess

import calliope.playlist

log = logging.getLogger(__name__)

__all__ = ['SyncException', 'sync']

class SyncException(RuntimeError):
    """Error that occured during ``sync()``."""


class Operation():
    '''Base class for operations that this tool can perform.'''
    def __str__(self):
        return ' '.join(self.cmdline())

    def cmdline(self):
        raise NotImplementedError()


class TranscodeToMP3Operation(Operation):
    '''Represesents transcoding to MP3 using GStreamer.'''
    def __init__(self, source_path, dest_path):
        self.source_path, self.dest_path = source_path, dest_path

    def cmdline(self):
        return ['gst-launch-1.0', '-t', 'filesrc', 'location="%s"' %
                str(self.source_path), '!', 'decodebin', '!', 'audioconvert', '!',
                'lamemp3enc', 'quality=0', '!', 'id3mux', '!', 'filesink',
                'location="%s"' % self.dest_path]

    def run(self):
        if not os.path.exists(os.path.dirname(self.dest_path)):
            os.makedirs(os.path.dirname(self.dest_path))
        if not os.path.exists(self.dest_path):
            subprocess.check_call(self.cmdline())


class CopyOperation(Operation):
    '''Represents a simple file copy.'''
    def __init__(self, source_path, dest_path, recursive=False):
        self.source_path, self.dest_path = source_path, dest_path
        self.recursive = recursive

    def cmdline(self):
        rsync_cmd = ['rsync', '--times']
        if self.recursive:
            rsync_cmd += ['--recursive']
        rsync_cmd += [str(self.source_path), str(self.dest_path)]
        return rsync_cmd

    def run(self):
        if not os.path.exists(os.path.dirname(self.dest_path)):
            os.makedirs(os.path.dirname(self.dest_path))
        if not os.path.exists(self.dest_path):
            try:
                subprocess.check_call(self.cmdline())
            except Exception as e:
                raise RuntimeError(e) from e


def ensure_number(filename, number):
    '''Ensure filename begins with 'number'.'''
    existing_number = ''.join(itertools.takewhile(str.isdigit, filename))
    if len(existing_number) == 0 or str(existing_number) != str(number):
        return '%03i_%s' % (number, filename)
    else:
        return filename


def make_dirname(*items):
    return '_'.join(filter(None, items))


def normalize_path(path):
    allowed = string.ascii_letters + string.digits + '._'
    return ''.join([char if char in allowed else '_' for char in path])


class SyncState():
    def __init__(self, target, allow_formats=None, number_files=False):
        self.target = pathlib.Path(target)
        self.allow_formats = allow_formats or ['all']
        self.number_files = number_files
        self.operations = []

    def sync_track(self, item, item_number=None):
        path = calliope.uri_to_path(item['location'])
        if not path.is_file():
            raise SyncException(
                f"Expected file for track '{item['track']}', got: {path}")

        if self.number_files:
            filename = ensure_number(path.name, item_number + 1)
        else:
            filename = None  # use existing

        operation = self.create_track_operation(path, target_filename=filename)
        self.operations.append(operation)

    def sync_album(self, item, item_number=None):
        path = calliope.uri_to_path(item['location'])
        if not path.is_dir():
            raise SyncException(
                f"Expected dir for album '{item['album']}', got: {path}")

        if self.number_files:
            filename = ensure_number(path.name, item_number + 1)
        else:
            filename = None  # use existing

        operation = self.create_album_operation(path, target_filename=filename)
        self.operations.append(operation)

    def create_track_operation(self, path, target_dirname=None,
                               target_filename=None):
        # We only look at the filename to determine file format, which is the
        # quickest method but not the most reliable.
        filetype = path.suffix.lstrip('.')

        if target_dirname:
            target_dirname = self.target.joinpath(target_dirname)
        else:
            target_dirname = self.target
        if not target_filename:
            target_filename = path.name

        if 'all' in self.allow_formats or filetype in self.allow_formats:
            sync_operation = CopyOperation(path, target_dirname.joinpath(target_filename))
        else:
            if 'mp3' not in self.allow_formats:
                raise NotImplementedError(
                    "File %s needs to be transcoded to an allowed format, but "
                    "only transcoding to MP3 is supported right now, and MP3 "
                    "doesn't seem to be allowed. Please allow MP3 files, or "
                    "improve this tool." % target_filename)
            else:
                if not target_filename.endswith('.mp3'):
                    target_filebasename = os.path.splitext(target_filename)[0]
                    target_filename = target_filebasename + '.mp3'
                sync_operation = TranscodeToMP3Operation(
                    path, target_dirname.joinpath(target_filename))
        return sync_operation

    def create_album_operation(self, path, target_dirname=None,
                               target_filename=None):
        # FIXME: we don't transcode or fix numbering or anything right now.
        # Code which used to do that is below.

        if target_dirname:
            target_dirname = self.target.joinpath(target_dirname)
        else:
            target_dirname = self.target
        if not target_filename:
            target_filename = path.name
        sync_operation = CopyOperation(str(path) + '/', target_dirname.joinpath(target_filename),
                                       recursive=True)
        return sync_operation
        #for track_number, track_item in enumerate(item['tracks']):
        #    if 'location' in track_item:
        #        path = calliope.uri_to_path(track_item['location'])
        #        if number_files:
        #            filename = ensure_number(
        #                os.path.basename(path),
        #                track_number + 1)
        #        else:
        #            filename = None  # use existing

        #        if album_per_dir:
        #            album_name = item.get('album') or 'No album'
        #            if number_dirs:
        #                dirname = make_dirname('%03i' % (item_number + 1),
        #                                        item['artist'],
        #                                        album_name)
        #            else:
        #                dirname = make_dirname(item['artist'],
        #                                        album_name)
        #        else:
        #            dirname = None  # use existing

        #        if filename:
        #            target_filename = normalize_path(filename)
        #        else:
        #            target_filename = None

        #        if dirname:
        #            target_dirname = normalize_path(dirname)
        #        else:
        #            target_dirname = None

        #        operations.append(
        #            sync_track(track_item['location'], target,
        #                        allow_formats,
        #                        target_filename=target_filename,
        #                        target_dirname=target_dirname))


def sync(dry_run: bool, target: pathlib.Path, allow_formats: [str],
         album_per_dir: bool, number_dirs: bool, number_files: bool,
         playlist: calliope.playlist.Playlist):
    """Copy items in `playlist` to `target`.

    The default for `allow_formats` is to allow all formats. You may instead
    set it to `['mp3']`, which will cause everything to be transcoded to .mp3
    format.

    Args:
        dry_run: print list of operations to stdout, instead of running them
        target: destination folder
        allow_formats: list of extensions to allow
        playlist: input playlist

    """
    state = SyncState(target, allow_formats, number_files)

    for item_number, item in enumerate(playlist):
        if 'location' in item:
            path = calliope.uri_to_path(item['location'])
            if path.is_file():
                state.sync_track(item, item_number)
            elif path.is_dir():
                state.sync_album(item, item_number)
            else:
                log.warning("Ignoring location %s", item['location'])
        else:
            log.warning("No location for item %s", item)

    if dry_run:
        for operation in state.operations:
            print(operation)
    else:
        for operation in state.operations:
            log.debug(str(operation))
            operation.run()
