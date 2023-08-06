# Calliope
# Copyright (C) 2018,2021  Sam Thursfield <sam@afuera.me.uk>
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


import logging
import sys

import calliope.playlist

from .compare import creator_equal, album_equal, song_equal, track_equal


log = logging.getLogger(__name__)


def diff(playlist_a, playlist_b, equal_function=None):
    """Calculate difference between two playlists.

    Playlists are sets of items. Two items are equal according
    to ``equal_function``. This function calculates set difference
    between ``playlist_a`` and ``playlist_b``, returning all items
    from ``playlist_a`` which do not have a counterpart in ``playlist_b``.

    """
    equal_function = equal_function or track_equal

    playlist_b = list(playlist_b)
    for a in playlist_a:
        if not any(equal_function(a,b) for b in playlist_b):
            yield a
