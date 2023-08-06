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


import enum
import logging

import calliope

from . import api
from . import listens

import calliope.subprojects.pylistenbrainz as pylistenbrainz


# corresponds to pylistenbrainz.PLAYLIST_QUERY_TYPE*
class PlaylistQueryType(enum.IntEnum):
    CREATED_BY = 0
    COLLABORATOR = 1
    CREATED_FOR = 2

    def to_pylistenbrainz_query_type(self):
        if self.value == self.CREATED_BY:
            return pylistenbrainz.PLAYLIST_QUERY_TYPE_CREATED_BY
        elif self.value == self.COLLABORATOR:
            return pylistenbrainz.PLAYLIST_QUERY_TYPE_COLLABORATOR
        elif self.value == self.CREATED_FOR:
            return pylistenbrainz.PLAYLIST_QUERY_TYPE_CREATED_FOR
        raise ValueError(f"Unexpected enum value: {self.value}")


log = logging.getLogger(__name__)

def playlists(user, kind):
    listenbrainz = pylistenbrainz.ListenBrainz()

    playlist_metas = []
    offset = 0
    while True:
        result = listenbrainz.get_user_playlists(
            username=user,
            query_type=kind.to_pylistenbrainz_query_type(),
            offset=0,
            count=api.MAX_ITEMS_PER_GET
        )
        playlist_metas.extend(result)
        if len(result) < api.MAX_ITEMS_PER_GET:
            break
        offset += api.MAX_ITEMS_PER_GET
    log.debug("Fetched metadata for %i playlists.", len(result))

    for meta in playlist_metas:
        playlist = listenbrainz.get_playlist(meta.identifier)
        yield from calliope.import_.process_jspf(playlist.to_jspf())
