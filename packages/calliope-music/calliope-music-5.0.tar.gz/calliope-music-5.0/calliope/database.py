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


import logging
import sqlite3
import time


def sqlite3_commit_with_retry(db: sqlite3.Connection, max_retries: int=3):
    for i in range(0, max_retries):
        try:
            db.commit()
            break
        except sqlite3.OperationalError as e:
            # Probably 'database is locked', we should retry a few times.
            logging.debug("%s, try %i of %i", e, i, max_retries)
            if i == max_retries:
                raise
            else:
                time.sleep(0.1)
