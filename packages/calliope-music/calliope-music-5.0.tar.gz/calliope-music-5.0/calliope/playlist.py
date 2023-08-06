# Calliope
# Copyright (C) 2016, 2018  Sam Thursfield <sam@afuera.me.uk>
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


import splitstream

import enum
import io
import json
import pathlib
import typing


class PlaylistError(RuntimeError):
    pass

class UnhashableItem(PlaylistError):
    pass


class PlaylistFormat(enum.Enum):
    """Playlist serialization formats.

      * ``XSPF``: `XML Shareable Playlist Format <https://www.xspf.org>`_
      * ``JSPF``: JSON variant of XSPF. Note that YAML is accepted as well.
      * ``CUE``: The `Cue sheet format <https://en.wikipedia.org/wiki/Cue_sheet_(computing)>`_
      * ``M3U``: M3U and Extended M3U. See `<https://en.wikipedia.org/wiki/M3U>`_
      * ``PLS``: The INI-based `PLS format <https://en.wikipedia.org/wiki/PLS_(file_format)>`_

    Check the :mod:`Import` and :mod:`Export` modules to see which formats
    they support.

    """
    CUE = 1
    JSPF = 2
    M3U = 3
    PLS = 1
    XSPF = 4


class Item(dict):
    '''Represents a single item in a Calliope playlist.'''
    def __init__(self, data=None):
        super().__init__(self)
        if data:
            self.update(data)

    def id(self):  # pylint: disable=invalid-name
        if 'calliope.id' in self:
            return self['calliope.id']
        elif 'id' in self:
            # deprecated as this doesn't follow the schema
            return self['id']
        elif 'creator' in self and 'title' in self:
            return '%s.%s' % (self.get('creator').lower(), self.get('title').lower())
        elif 'creator' in self and 'album' in self:
            return '%s.%s' % (self.get('creator').lower(), self.get('album').lower())
        else:
            # It's not going to be hashable in this case.
            raise UnhashableItem(
                f"Could not create hash for item with fields: {self.keys()}")

    def __hash__(self):
        return hash(self.id())

    def __str__(self):
        try:
            return f"𝄞{self.id()} ({len(self)})"
        except UnhashableItem:
            return "𝄞?"

    def add_warning(self, namespace, message):
        warnings = self.get('meta.warnings', [])
        warnings.append(f"{namespace}: {message}")
        self['meta.warnings'] = warnings
        return self


Playlist = typing.NewType('Playlist', [Item])


def read(stream):
    '''Parses a playlist from the given stream.

    Returns an generator that produces calliope.playlist.Item objects.

    The generator will read from the file on demand, so you must be careful not
    to do this:

        with open('playlist.cpe', 'r') as f:
            playlist = calliope.playlist.read(f)

        for item in playlist:
            # You will see 'ValueError: I/O operation on closed file.'.
            ...

    If you want to read the playlist in one operation, convert it to a list:

        with open('playlist.cpe', 'r') as f:
            playlist = list(calliope.playlist.read(f))

    '''
    # FIXME: this works around a brainfart in click.testing and splitstream.
    # The former mandates that stdin is a textiowrapper and the latter
    # breaks if stdin is a textiowrapper.
    if isinstance(stream, io.TextIOWrapper):
        stream = stream.detach()
    for text in splitstream.splitfile(stream, format='json'):
        try:
            json_document = json.loads(text)
        except ValueError as e:
            raise PlaylistError(f"Error parsing {stream.name}: {e}") from e
        if isinstance(json_document, dict):
            yield Item(json_document)
        elif isinstance(json_document, list):
            yield from (Item(item) for item in json_document)
        else:
            raise PlaylistError("Expected JSON object, got {}".format(type(json_document).__name__))


def write(items, stream):
    '''Write a playlist to the given stream.'''
    for item in items:
        json.dump(item, stream)
        stream.write('\n')


def split(items):
    '''Convert a list of items into a list of playlists.

    Splitting is done based on the `playlist.title` attribute. Each time an
    item is found with this attribute set, it's treated as a new playlist.

    '''
    def is_new_playlist(item):
        return 'playlist.title' in item
    items = iter(items)
    current_playlist = []
    while True:
        try:
            item = next(items)
        except StopIteration:
            if len(current_playlist) > 0:
                yield current_playlist
            break
        if is_new_playlist(item) and len(current_playlist) > 0:
            yield current_playlist
            current_playlist = [item]
        else:
            current_playlist.append(item)


def load_schema() -> dict:
    """Returns the JSON Schema for Calliope playlist items."""
    module_path = pathlib.Path(__file__).parent
    schema = module_path.joinpath('playlist-item.jsonschema')
    return json.loads(schema.read_text())
