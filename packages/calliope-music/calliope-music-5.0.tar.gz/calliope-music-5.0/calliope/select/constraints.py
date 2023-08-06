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


import logging
import random

import calliope.playlist


def linear_score(value, vmin, vmax):
    """Objective function for `value` and target range [`vmin`, `vmax`]

    Returns 1.0 if vmin <= value <= vmax, decreasing linearly to 0.0 as
    value tends towards 0.0 and vmax*2.

    """
    if vmin > 0 and value <= vmin:
        score = value / vmin
    elif value >= vmax:
        score = max((-value + (2 * vmax)), 0) / vmax
    else:
        score = 1.0
    return score


class Constraint():
    """Abstract base class."""
    def __init__(self):
        self.log = logging.getLogger(self.__class__.__name__)

    def __repr__(self):
        return f"<{self.__class__.__name__}>"


class ItemConstraint(Constraint):
    def __init__(self, prop: str):
        super().__init__()
        self.prop = prop

    def __repr__(self):
        return f"<{self.__class__.__name__}({self.prop})>"

    def score_item(self, item: calliope.playlist.Item) -> float:
        """Score how well `item` satisfies this constraint.

        The score must be between 0.0 (doesn't satisfy constraint) and 1.0
        (satisfies it perfectly).

        """
        raise NotImplementedError()

    def partition(self, collection) -> [[calliope.playlist.Item]]:
        """Divide 'collection' into one 'good' and one or more 'bad' groups.

        This is used to define the neighbourhood we search for a solution.

        """
        raise NotImplementedError()


class GlobalConstraint(Constraint):
    """Abstract base class for global (whole playlist) constraints."""

    def score_playlist(self, playlist):
        """Score how well `playlist` satisfies this constraint.

        The score must be between 0.0 (doesn't satisfy constraint) and 1.0
        (satisfies it perfectly).

        """
        raise NotImplementedError()


#
# Generic constraint types
#


class SetConstraint(ItemConstraint):
    def __init__(self, prop: str, values: [str]):
        """Simple set constraint, for properties with nominal (string) values.

        An item satisfies the constraint if its value matches one member of
        `values`.

        """
        super().__init__(prop)
        self.values = set(values)

    def __repr__(self):
        return f"<{self.__class__.__name__}({self.prop} in {self.values})>"

    def score_item(self, item: calliope.playlist.Item) -> float:
        value = item[self.prop]
        if value in self.values:
            score = 1.0
        else:
            score = 0.0
        self.log.debug("Scoring item with %s=%s as %f", self.prop, value, score)
        return score

    def partition(self, collection):
        try:
            good = [s for s in collection if s[self.prop] in self.values]
            bad = [s for s in collection if s[self.prop] not in self.values]
        except KeyError as e:
            # It would be nice if we could say *which* item...
            raise KeyError(
                f"Property {e.args[0]} not set on one or more playlist items.") from e
        return good, bad


class RangeConstraint(ItemConstraint):
    def __init__(self, prop: str, vmin: float, vmax: float):
        """Simple range constraint, for properties with numeric values.

        An item scores 1.0 if `vmin` <= `prop` <= `vmax`. The score decreases
        linearly towards 0.0 as `prop` approaches 0 or 2*`vmax`.

        t's common to specify a single value by specifying `vmin` = `vmax`.

        """
        super().__init__(prop)
        self.vmin = float(vmin)
        self.vmax = float(vmax)
        assert self.vmax > 0
        assert self.vmax >= self.vmin

    def __repr__(self):
        if self.vmin == self.vmax:
            return f"<{self.__class__.__name__}({self.prop}={self.vmax})>"
        else:
            return f"<{self.__class__.__name__}({self.vmin}<={self.prop}<={self.vmax})>"

    def score_item(self, item):
        value = item[self.prop]
        score = linear_score(value, self.vmin, self.vmax)
        self.log.debug("Scoring item with %s=%s as %f", self.prop, value, score)
        return score

    def partition(self, collection):
        try:
            good = [s for s in collection if s[self.prop] >= self.vmin and s[self.prop] <= self.vmax]
            too_low = [s for s in collection if s[self.prop] < self.vmin]
            too_high = [s for s in collection if s[self.prop] > self.vmax]
        except KeyError as e:
            # It would be nice if we could say *which* item...
            raise calliope.select.SelectError(
                f"Property {e.args[0]} not set on one or more playlist items.") from e
        except TypeError as e:
            raise calliope.select.SelectError(
                f"Type error for property '{self.prop}': {e}") from e
        # It's probably important that we don't have all the low values before
        # all the high values.
        bad = too_low + too_high
        random.shuffle(bad)
        return good, bad


class EachGlobalConstraint(GlobalConstraint):
    """Apply an item constraint to every item in the playlist."""

    def __init__(self, item_constraint: ItemConstraint):
        super().__init__()
        self.item_constraint = item_constraint

    def __repr__(self):
        return f"<{self.__class__.__name__}({self.item_constraint})>"

    def score_playlist(self, playlist):
        if len(playlist) == 0:
            self.log.debug("Scoring empty playlist as 0.0")
            return 0.0     # Empty playlist is not a useful output.
        else:
            total = sum(self.item_constraint.score_item(s)
                        for s in playlist)
            score = total / len(playlist)
            self.log.debug("Scoring playlist with %i/%i satisfactory songs as %f",
                           total, len(playlist), score)
            return score

    def partition(self, collection):
        return self.item_constraint.partition(collection)


class FractionGlobalConstraint(GlobalConstraint):
    """Apply an item set constraint to some items in the playlist."""

    def __init__(self, item_constraint: SetConstraint, fmin: float, fmax: float):
        super().__init__()
        self.item_constraint = item_constraint
        self.fmin = float(fmin)
        self.fmax = float(fmax)

    def __repr__(self):
        return f"<{self.__class__.__name__}({self.item_constraint},{self.fmin},{self.fmax})>"

    def score_playlist(self, playlist):
        if len(playlist) == 0:
            self.log.debug("Scoring empty playlist as 0.0")
            score = 0.0     # Empty playlist is not a useful output.
        else:
            # This uses a set constraint, so score will be 0.0 or 1.0 only.
            total_matching = sum(self.item_constraint.score_item(s) for s in playlist)
            value = total_matching / len(playlist)
            score = linear_score(value, self.fmin, self.fmax)
            self.log.debug("Scoring playlist with fraction %f (%s/%s items matching) as %f",
                           value, total_matching, len(playlist), score)
        return score

    def partition(self, collection):
        return self.item_constraint.partition(collection)


class SumGlobalConstraint(GlobalConstraint, RangeConstraint):
    """The sum of 'prop' for all songs should be between 'vmin' and 'vmax'."""

    def __init__(self, prop, vmin, vmax):
        GlobalConstraint.__init__(self)
        RangeConstraint.__init__(self, prop, vmin, vmax)

    def __repr__(self):
        return f"<{self.__class__.__name__}({self.vmin}<sum({self.prop})<{self.vmax})>"

    def score_playlist(self, playlist):
        value = sum(s[self.prop] for s in playlist)
        score = linear_score(value, self.vmin, self.vmax)
        self.log.debug("Scoring playlist with sum(%s)=%s as %f", self.prop, value, score)
        return score

    def partition(self, collection):
        # There's no way I can see to usefully partition data for a sum-global
        # constraint, so assume anything is worth trying.
        return collection, []


#
# Specific constraint types
#



class ItemDurationConstraint(EachGlobalConstraint):
    """Each song should have duration in range [min, max]."""
    PROP = 'duration'
    def __init__(self, vmin, vmax):
        item_constraint = RangeConstraint(self.PROP, vmin, vmax)
        super().__init__(item_constraint)


class PlaylistDurationConstraint(SumGlobalConstraint):
    """Playlist should be a specified number of seconds in duration."""
    PROP = 'duration'
    def __init__(self, vmin, vmax):
        super().__init__(self.PROP, vmin, vmax)


class PlaylistDiskSpaceConstraint(SumGlobalConstraint):
    """Playlist items should total a specified number of bytes in size."""
    PROP = 'album.size_mb'
    def __init__(self, vmin, vmax):
        super().__init__(self.PROP, vmin, vmax)


#
# Names (for parser)
#

BY_NAME = {
    'set': SetConstraint,
    'range': RangeConstraint,
    'each-global': EachGlobalConstraint,
    'fraction-global': FractionGlobalConstraint,
    'sum-global': SumGlobalConstraint,
    'item-duration': ItemDurationConstraint,
    'playlist-duration': PlaylistDurationConstraint,
    'playlist-disk-space': PlaylistDiskSpaceConstraint,
}
