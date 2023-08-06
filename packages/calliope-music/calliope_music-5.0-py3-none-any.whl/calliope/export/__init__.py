# Calliope
# Copyright (C) 2016,2018-2019  Sam Thursfield <sam@afuera.me.uk>
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


"""Convert playlists to different serialization formats.

See also: :program:`cpe export` command.

"""

import calliope.playlist

import itertools
import json
import pathlib
import re
import unicodedata
import warnings
import xml.dom.minidom
import xml.etree.ElementTree


def get_format_id(name):
    try:
        return calliope.playlist.PlaylistFormat[name.upper()]
    except KeyError as e:
        raise NotImplementedError(f"Format '{format}' isn't supported") from e


def convert_to_cue(playlist):
    output_text = ['FILE "none" WAVE']
    for i, item in enumerate(playlist):
        output_text.append("  TRACK %02i AUDIO" % (i + 1))
        if 'title' in item:
            output_text.append("    TITLE \"%s\"" % item['title'])
        if 'creator' in item:
            output_text.append("    PERFORMER \"%s\"" % item['creator'])
        if 'play.start_time' in item:
            timestamp = item['play.start_time']
        else:
            if i == 0:
                timestamp = 0
            else:
                raise RuntimeError("The 'play.start_time' field must be set for all entries "
                                   "in order to create a CUE sheet")
        output_text.append("  INDEX 01 %02i:%02i:00" % (int(timestamp / 60), int(timestamp % 60)))
    return '\n'.join(output_text)


def convert_to_m3u(playlist, title=None, location_required=False, extended=True):
    output_text = []

    for i, item in enumerate(playlist):
        if i == 0:
            if extended:
                output_text.append('#EXTM3U')
                title = title or item.get('playlist.title')
                if title:
                    output_text.append(f'#PLAYLIST:{title}')
                image = item.get('playlist.image')
                if image:
                    output_text.append(f'#EXTIMG:{image}')

        if 'location' in item:
            output_text.append(item['location'])
        elif location_required:
            raise RuntimeError("The 'location' field must be set for all entries "
                                "in order to create an M3U playlist")
        else:
            warnings.warn(f"Location field not set for {item}")

    return '\n'.join(output_text)


def convert_to_jspf(playlist, title=None):
    doc = {}

    # We honour playlist metadata if we find it on the first playlist entry.
    try:
        first_entry = next(playlist)
    except StopIteration as e:
        raise RuntimeError("Tried to export an empty playlist.") from e

    def calliope_to_jspf(calliope_entry, jspf_entry, calliope_property, jspf_property, convert_fn=str):
        if calliope_property in calliope_entry:
            jspf_entry[jspf_property] = convert_fn(calliope_entry[calliope_property])

    if title:
        doc['title'] = title
    else:
        calliope_to_jspf(first_entry, doc, 'playlist.title', 'title')
    calliope_to_jspf(first_entry, doc, 'playlist.creator', 'creator')
    calliope_to_jspf(first_entry, doc, 'playlist.annotation', 'annotation')
    calliope_to_jspf(first_entry, doc, 'playlist.info', 'info')
    calliope_to_jspf(first_entry, doc, 'playlist.location', 'location')
    calliope_to_jspf(first_entry, doc, 'playlist.identifier', 'identifier')
    calliope_to_jspf(first_entry, doc, 'playlist.image', 'image')
    calliope_to_jspf(first_entry, doc, 'playlist.date', 'date')
    calliope_to_jspf(first_entry, doc, 'playlist.license', 'license')

    tracklist = []

    for entry in itertools.chain([first_entry], playlist):
        track = {}
        calliope_to_jspf(entry, track, 'location', 'location')
        calliope_to_jspf(entry, track, 'identifier', 'identifier')
        calliope_to_jspf(entry, track, 'title', 'title')
        calliope_to_jspf(entry, track, 'creator', 'creator')
        calliope_to_jspf(entry, track, 'annotation', 'annotation')
        calliope_to_jspf(entry, track, 'info', 'info')
        calliope_to_jspf(entry, track, 'image', 'image')
        calliope_to_jspf(entry, track, 'album', 'album')
        calliope_to_jspf(entry, track, 'trackNum', 'trackNum')
        calliope_to_jspf(entry, track, 'duration', 'duration',
                         # Convert seconds to whole milliseconds
                         convert_fn=lambda d: str(int(d * 1000)))
        tracklist.append(track)

    doc['track'] = tracklist

    return json.dumps({
        'playlist': doc
    }, indent=4)


def convert_to_xspf(playlist, title=None):
    NAMESPACE = 'http://xspf.org/ns/0/'

    # Avoid namespace prefixes. VLC doesn't like it, according to
    # https://github.com/alastair/xspf/blob/master/xspf.py.
    xml.etree.ElementTree.register_namespace('', NAMESPACE)

    def namespaced_tag(name):
        return "{{{0}}}{1}".format(NAMESPACE, name)

    root = xml.etree.ElementTree.Element(namespaced_tag('playlist'))
    root.set('version', '1')

    # We honour playlist metadata if we find it on the first playlist entry.
    try:
        first_entry = next(playlist)
    except StopIteration as e:
        raise RuntimeError("Tried to export an empty playlist.") from e

    def calliope_to_xspf(entry, element, calliope_property, xspf_tag, convert_fn=str):
        if calliope_property in entry:
            sub_element = xml.etree.ElementTree.SubElement(element, namespaced_tag(xspf_tag))
            sub_element.text = convert_fn(entry[calliope_property])

    if title:
        xml.etree.ElementTree.SubElement(root, namespaced_tag('title')).text = title
    else:
        calliope_to_xspf(first_entry, root, 'playlist.title', 'title')
    calliope_to_xspf(first_entry, root, 'playlist.creator', 'creator')
    calliope_to_xspf(first_entry, root, 'playlist.annotation', 'annotation')
    calliope_to_xspf(first_entry, root, 'playlist.info', 'info')
    calliope_to_xspf(first_entry, root, 'playlist.location', 'location')
    calliope_to_xspf(first_entry, root, 'playlist.identifier', 'identifier')
    calliope_to_xspf(first_entry, root, 'playlist.image', 'image')
    calliope_to_xspf(first_entry, root, 'playlist.date', 'date')
    calliope_to_xspf(first_entry, root, 'playlist.license', 'license')

    tracklist = xml.etree.ElementTree.SubElement(root, namespaced_tag('trackList'))

    for entry in itertools.chain([first_entry], playlist):
        track = xml.etree.ElementTree.SubElement(tracklist, namespaced_tag('track'))
        calliope_to_xspf(entry, track, 'location', 'location')
        calliope_to_xspf(entry, track, 'identifier', 'identifier')
        calliope_to_xspf(entry, track, 'title', 'title')
        calliope_to_xspf(entry, track, 'creator', 'creator')
        calliope_to_xspf(entry, track, 'annotation', 'annotation')
        calliope_to_xspf(entry, track, 'info', 'info')
        calliope_to_xspf(entry, track, 'image', 'image')
        calliope_to_xspf(entry, track, 'album', 'album')
        calliope_to_xspf(entry, track, 'trackNum', 'trackNum')
        calliope_to_xspf(entry, track, 'duration', 'duration',
                         # Convert seconds to whole milliseconds
                         convert_fn=lambda d: str(int(d * 1000)))

    # In the name of beauty, we serialize with xml.etree and then
    # reformat it with xml.dom.minidom to get indentation and newlines.
    text = xml.etree.ElementTree.tostring(root, 'utf-8')
    dom = xml.dom.minidom.parseString(text)
    return dom.toprettyxml(indent='\t')


def default_title_to_filename_fn(title, format_id):
    # Based on Django `slugify()` function.
    # See https://stackoverflow.com/a/295466/10433384
    value = unicodedata.normalize('NFKD', title).encode('ascii', 'ignore')
    value = re.sub(r'[^\w\s-]', '', title).strip().lower()
    value = re.sub(r'[-\s]+', '-', title)
    extension = format_id.name.lower()
    return value + f'.{extension}'


def export_single_playlist(playlist, format_id, title=None):
    """Export to text using the given serialization format.

    The supported formats are: CUE, M3U, JSPF and XSPF.

    """
    if format_id == calliope.playlist.PlaylistFormat.CUE:
        if title:
            raise RuntimeError("CUE format does not support setting a title.")
        return convert_to_cue(playlist)
    elif format_id == calliope.playlist.PlaylistFormat.M3U:
        return convert_to_m3u(playlist, title=title, extended=True)
    elif format_id == calliope.playlist.PlaylistFormat.JSPF:
        return convert_to_jspf(playlist, title=title)
    elif format_id == calliope.playlist.PlaylistFormat.XSPF:
        return convert_to_xspf(playlist, title=title)
    else:
        raise NotImplementedError("Unsupport format: %s" % format)


def export_many_playlists(playlists, format_id, path, filename_fn=None):
    """Export multiple playlists.

    Each item with the `playlist.title` attribute set is treated as the first
    item in a new playlist.

    """
    path = pathlib.Path(path)
    filename_fn = filename_fn or default_title_to_filename_fn
    for i, playlist in enumerate(playlists):
        first_item = playlist[0]
        title = first_item.get('playlist.title', f"Playlist {i}")
        filename = filename_fn(title, format_id)
        with open(path.joinpath(filename), 'w') as f:
            calliope.playlist.write(playlist, f)
