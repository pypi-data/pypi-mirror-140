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


"""Resolve Musicbrainz identifiers from playlist data."""


import logging

import musicbrainzngs

from calliope import playlist
from .context import MusicbrainzContext

log = logging.getLogger(__name__)


def _try_pop_first(iterable):
    try:
        return iterable.pop(0)
    except IndexError:
        return None

def release_ids_from_album(context: MusicbrainzContext, item: playlist.Item) \
        -> playlist.Item:
    """Identify the Musicbrainz release representing ``item``.

    Uses the ``musicbrainzngs.search_releases()`` method to find matching
    `Musicbrainz Release entity <https://musicbrainz.org/doc/Release>`_.

    Any of the following properties will be used in the search, if set:

      * ``creator``
      * ``album``
      * ``musicbrainz.artist_id``

    All of the following properties will be set in the output:

      * ``musicbrainz.artist_id``
      * ``musicbrainz.release_id``
      * ``musicbrainz.release_group_id``

    Note that the ``musicbrainz.artist_id`` property will correspond to the
    whole album.

    """
    INPUT_PROPERTIES = [
        'creator',
        'album',
        'musicbrainz.artist_id',
    ]

    OUTPUT_PROPERTIES = [
        'musicbrainz.artist_id',
        'musicbrainz.release_id',
        'musicbrainz.release_group_id',
    ]

    item = playlist.Item(item)

    if not any(p in item for p in INPUT_PROPERTIES):
        return item
    if all(p in item for p in OUTPUT_PROPERTIES):
        return item

    release_name = item['album']
    artist_id = item.get('musicbrainz.artist_id')
    artist_name = item.get('creator')

    if artist_id:
        key = 'album:{}:{}'.format(artist_id, release_name)
        query = 'arid:{} {}'.format(artist_id, release_name)
    elif artist_name:
        key = 'album:{}:{}'.format(artist_name, release_name)
        query = ' AND '.join(artist_name.split() + release_name.split())
    else:
        key = 'album:{}'.format(release_name)
        query = '{}'.format(release_name)

    release = context.cache.wrap(key, lambda: _try_pop_first(
        musicbrainzngs.search_releases(query)['release-list']))

    if release is None:
        item.add_warning('musicbrainz', "Unable to find release on musicbrainz")
    else:
        item['musicbrainz.artist_id'] = release['artist-credit'][0]['artist']['id']
        item['musicbrainz.release_id'] = release['id']
        item['musicbrainz.release_group_id'] = release['release-group']['id']

    return item


def _get_front_image_url(image_list, max_size):
    for image in image_list['images']:
        if image['front'] is True:
            thumbs = image['thumbnails']
            if max_size is not None:
                if str(max_size) in thumbs:
                    return thumbs[str(max_size)]
                elif str(max_size) == '250' and 'small' in thumbs:
                    return thumbs['small']
                elif str(max_size) == '500' and 'large' in thumbs:
                    return thumbs['large']
            return image['image']
    return None


def image_for_item(context: MusicbrainzContext,
                   item: playlist.Item,
                   max_size: int) -> playlist.Item:
    item = release_ids_from_album(context, item)
    release_id = item.get('musicbrainz.release_id')
    if release_id:
        try:
            key = 'release:{}:image_list'.format(release_id)
            image_list = context.cache.wrap(key,
                lambda: musicbrainzngs.get_image_list(release_id))
            image = _get_front_image_url(image_list, max_size)
            if image:
                item['image'] = image
        except musicbrainzngs.musicbrainz.ResponseError as e:
            log.debug("No image for %s: %s", release_id, e)
    return item
