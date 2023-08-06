# Calliope
# Copyright (C) 2019,2020  Sam Thursfield <sam@afuera.me.uk>
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


import jsonschema

import calliope.playlist


class ValidationError(RuntimeError):
    pass


def validate(playlist):
    schema = calliope.playlist.load_schema()
    try:
        if isinstance(playlist, list):
            for item in playlist:
                jsonschema.validate(instance=item, schema=schema)
        else:
            jsonschema.validate(instance=playlist, schema=schema)
    except jsonschema.ValidationError as e:
        raise ValidationError(e) from e
