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


import musicbrainzngs

import calliope.cache


class MusicbrainzContext():
    """Configuration for Musicbrainz APIs.

    Keys used from ``config`` dict:

      * ``musicbrainz.app``: App name
      * ``musicbrainz.version``: API version
      * ``musicbrainz.contact``: Contact URL

    If unset, the defaults reference Calliope and API version 1.
    """

    def __init__(self, config: dict):
        self.config = config

        app = config.get('musicbrainz', 'app') or "Calliope"
        version = config.get('musicbrainz', 'version') or "1"
        contact = config.get('musicbrainz', 'contact') or \
                  "https://gitlab.com/samthursfield/calliope"

        musicbrainzngs.set_useragent(app, version, contact)

        self.cache = calliope.cache.open(namespace='musicbrainz')
