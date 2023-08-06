# Calliope
# Copyright (C) 2017-2021  Sam Thursfield <sam@afuera.me.uk>
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

"""Access data from `Musicbrainz <https://musicbrainz.org/>`_.

See also: :program:`cpe musicbrainz` command.

This module wraps the `musicbrainzngs <https://python-musicbrainzngs.readthedocs.io>`_ library.

Authentication
--------------

Musicbrainz access requires that you set a User Agent string. A default is set
by the :obj:`MusicbrainzContext` object which can be overridden using its
config.

Caching
-------

Caching of data is handled using the :mod:`calliope.cache` module.

"""

import logging

import musicbrainzngs

import calliope.cache
import calliope.config
import calliope.playlist
from . import annotate_helpers, resolve
from .context import MusicbrainzContext

log = logging.getLogger(__name__)


def annotate(context: MusicbrainzContext,
             playlist: calliope.playlist.Playlist,
             include: [str],
             select_fun=None,
             update=False):
    """Annotate each item in a playlist with metadata from Musicbrainz."""
    for item in playlist:
        match = annotate_helpers.search(context, item, select_fun=select_fun)
        if match is not None:
            for key, v in match.items():
                if key.startswith("musicbrainz.") or (update and "." not in key):
                    item[key] = v
            item["calliope.musicbrainz.resolver_score"] = match["_.priority"]

        if 'areas' in include:
            item = annotate_helpers.add_musicbrainz_artist_areas(context.cache, item)

        if 'release' in include:
            item = annotate_helpers.add_musicbrainz_album_release(context.cache, item)

        if 'urls' in include:
            item = annotate_helpers.add_musicbrainz_artist_urls(context.cache, item)

        yield item


def resolve_image(context: MusicbrainzContext,
                  playlist: calliope.playlist.Playlist,
                  max_size: int=250):
    """Resolve a cover image using the Cover Art API.

    See https://musicbrainz.org/doc/Cover_Art_Archive/API for more info."""

    assert str(max_size) in ['250', '500', 'None']

    for item in playlist:
        if 'image' not in item:
            item = resolve.image_for_item(context, item, max_size)
        yield item
