# Calliope
# Copyright (C) 2020  Sam Thursfield <sam@afuera.me.uk>
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


"""Select tracks for a playlist based on a set of constraints.

This module was inspired by the 2008 paper
`Music playlist generation by adapted simulated annealing
<https://www.researchgate.net/publication/223327847_Music_playlist_generation_by_adapted_simulated_annealing>`_
(S. Pauws, W. Verhaegh, M. Vossen).

See :mod:`calliope.select.constraints` for details of the constraints.
"""

import calliope.playlist

import logging
import re

from . import constraints
from . import localsearch

log = logging.getLogger(__name__)


class SelectError(Exception):
    """Exception returned from :mod:`calliope.select` module."""



def _load_collection(playlist):
    # We use a list and not a set() so that results can be deterministic.
    # The order of items when iterating a set() seems to be different per
    # execution even when the input playlist and the random.seed() value are
    # the same. For reliable testing, we must have deterministic behaviour.
    music_collection = []
    for i, item in enumerate(playlist):
        # Temporary workaround -- it might be better to generate
        # 'universal' ids from track metadata, in future.
        if 'calliope.id' not in item:
            item['calliope.id'] = str(i)
        music_collection.append(item)
    return music_collection


class ConstraintStringParseError(SelectError):
    """Error returned by :func:`constraint_from_string`."""


class _ConstraintStringParser():
    """Parse a string of key/value pairs as a constraint.

    The key/value format can be awkward to work with and is intended for
    commandline and testing use.

    """
    def lookup_kind(self, kind: str) -> object:
        try:
            return constraints.BY_NAME[kind]
        except KeyError as e:
            raise ConstraintStringParseError(f"Unknown constraint type {kind}", self.text) from e

    def instantiate(self, klass, params) -> constraints.Constraint:
        try:
            return klass(**params)
        except TypeError as e:
            raise ConstraintStringParseError(
                f"Error creating '{klass}' constraint: {e}", self.text) from e

    def parse_value(self, key: str, value: str):
        # Hardcoding all these params is pretty lame
        # Using the 'typing' module we could make something really cool.
        if key == 'values':
            return value.split(';')

        # FIXME: due to my laziness, we allow time values as input to any
        # range constraint, even where it doesn't make sense.
        if key in ['vmin', 'vmax']:
            match = re.match(r'(\d+)(s|sec|second|seconds)', value)
            if match:
                return float(match.group(1)) * 1000
            match = re.match(r'(\d+)(m|min|minute|minutes)', value)
            if match:
                return float(match.group(1)) * 1000 * 60
            match = re.match(r'(\d+)(h|hr|hrs|hourZhours)', value)
            if match:
                return float(match.group(1)) * 1000 * 60 * 60
            match = re.match(r'(\d+)(d|day|days)', value)
            if match:
                return float(match.group(1)) * 1000 * 60 * 60 * 24
            match = re.match(r'(\d+)(w|wk|wks|week|weeks)', value)
            if match:
                return float(match.group(1)) * 1000 * 60 * 60 * 24 * 7
            # That should be enough for anybody...
            try:
                return float(value)
            except ValueError as e:
                raise ConstraintStringParseError(
                    f"Could not parse {key}:{value}: {e}") from e

        return value

    def parse(self, text: str) -> constraints.Constraint:
        self.text = text  # pylint: disable=attribute-defined-outside-init
        pairs = text.split(',')

        kinds = []
        params = {}
        for pair in pairs:
            try:
                key, value = pair.split(':', 1)
            except ValueError as e:
                raise ConstraintStringParseError(f"Error parsing {pair}", self.text) from e
            if key == 'type':
                kinds = value.split(';')
            elif key == 'property':
                # We don't use 'property' internally as it's a Python keyword
                params['prop'] = value
            else:
                params[key] = self.parse_value(key, value)

        result = None
        if len(kinds) == 1:
            klass = self.lookup_kind(kinds[0])
            result = self.instantiate(klass, params)
        elif len(kinds) == 2:
            global_klass = self.lookup_kind(kinds[0])
            item_klass = self.lookup_kind(kinds[1])

            # It's not ideal that we hardcode global parameter names here, but,
            # at least the code is simple.
            global_keys = ['fmin', 'fmax']
            global_params = {}
            for key in global_keys:
                value = params.pop(key, None)
                if value:
                    global_params[key] = value
            item_params = params

            item_constraint = self.instantiate(item_klass, item_params)
            global_params['item_constraint'] = item_constraint
            result = self.instantiate(global_klass, global_params)
        else:
            raise ConstraintStringParseError(
                "Wrong number of `type` values given: got {}".format(len(kinds)),
                self.text)
        return result


def constraint_from_string(text: str) -> constraints.Constraint:
    parser = _ConstraintStringParser()
    return parser.parse(text)


def select(playlist: calliope.playlist.Playlist, constraints: [constraints.Constraint]) -> calliope.playlist.Playlist:
    """Select music from input playlist according to a set of constraints.

    A simple constraint solving algorithm is used to produce a playlist.
    This involves some random choices, which may produce different results
    each time the function is called unless the same random seed is used.

    See also: :command:`cpe select`.

    Args:
        playlist: input songs (order isn't important)
        constraints: one or more Constraint instances

    Returns:
        A playlist that satisfies the constraints.

    """
    if len(constraints) == 0:
        raise SelectError("You must supply one or more constraints.")

    music_collection = _load_collection(playlist)
    log.debug("Loaded collection with %i items", len(music_collection))

    log.debug("Creating problem with: %s", constraints)
    problem = localsearch.PlaylistGenerationProblem(music_collection, constraints, initial_length=6)

    result = localsearch.solve(problem)

    comments = [f"Generated by {__file__}"]
    if len(result.state) > 0:
        first_track = result.state[0]
        first_track['playlist.comments'] = comments
    return result.state
