# Calliope
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


"""Access data from `Bandcamp <https://bandcamp.com/>`_.

This module wraps a local fork of the
`bandcamp_api <https://github.com/Virusmater/bandcamp_api>`_ library.

Authentication
--------------

All the APIs used by this module can be accessed without authentication.

Caching
-------

HTTP requests are not cached. At time of writing, ``api.bandcamp.com`` requests
send the HTTP header ``Cache-Control: no-cache, no-store``.
"""

import logging
import sys

import calliope.cache
import calliope.config
import calliope.playlist
import calliope.subprojects.bandcamp_api as bandcamp_api

log = logging.getLogger(__name__)


class BandcampContext():
    def __init__(self, config: calliope.config.Configuration, user: str=None):
        """Context for accessing Bandcamp API.

        Args:
            user: Default user for requests

        """
        self.config = config

        if not user:
            user = self.config.get('bandcamp', 'user')
        if not user:
            raise RuntimeError("Please specify a username.")

        self.user = user
        log.debug("Bandcamp user: {}".format(user))

        self.api = bandcamp_api.bandcamp.Bandcamp(self.user)

    def get_fan_id(self):
        return self.api.get_fan_id()


def collection(bandcamp: BandcampContext,
               count=1000) -> calliope.playlist.Playlist:
    """Export all albums in Bandcamp collection."""
    bands = bandcamp.api.get_collection(bandcamp.get_fan_id(), count=count)

    for band in bands:
        for album in bands[band]:
            yield {
                'album': album.album_name,
                'bandcamp.album_id': album.album_id,
                'location': album.album_url,
                'creator': band.band_name,
                'bandcamp.artist_id': band.band_id
            }
