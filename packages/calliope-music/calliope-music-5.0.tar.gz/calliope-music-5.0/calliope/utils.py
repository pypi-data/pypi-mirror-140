# Calliope
# Copyright (C) 2021  Kilian Lackhove <kilian@lackhove.de>
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


"""
Utility functions for resolving items
"""

import re
from datetime import date
from enum import Enum, auto
from typing import Dict, Iterable, Optional, Tuple

from calliope.playlist import Item


class FeatMode(Enum):
    KEEP = auto()
    DROP = auto()
    TO_CREATOR = auto()
    TO_TITLE = auto()


def normalize_creator_title(
    creator: Optional[str], title: Optional[str], feat_mode=FeatMode.TO_CREATOR
) -> Tuple[Optional[str], Optional[str]]:
    """
    Remove featuring artists from title and append them to the artist string
    """

    short_title = None
    feat_title = None
    if title is not None:
        m = re.match(r"(.*?)\(?feat\.(.*)\)?", title, flags=re.IGNORECASE)
        if m is not None:
            short_title = m.group(1).strip()
            feat_title = m.group(2).strip()

    short_creator = None
    feat_creator = None
    if creator is not None:
        if creator.casefold().endswith(", the"):
            creator = "The " + creator[:-5]
        m = re.match(r"(.*?)?feat\.(.*)?", creator, flags=re.IGNORECASE)
        if m is not None:
            short_creator = m.group(1).strip()
            feat_creator = m.group(2).strip()

    if feat_mode is FeatMode.KEEP:
        pass
    elif feat_mode is FeatMode.TO_CREATOR:
        if feat_title is not None:
            creator = f"{creator or ''} {feat_title}".strip()
        title = short_title or title
    elif feat_mode is FeatMode.TO_TITLE:
        creator = short_creator or creator
        if feat_creator is not None:
            title = f"{title or ''} (feat. {feat_creator})".strip()
    elif feat_mode is FeatMode.DROP:
        creator = short_creator or creator
        title = short_title or title
    else:
        raise NotImplementedError()

    return creator, title


def drop_none_values(dct: Item) -> Item:
    """
    Delete all fields with None value from dct.
    """
    drop_keys = []
    for k, v in dct.items():
        if v is None:
            drop_keys.append(k)

    for k in drop_keys:
        del dct[k]

    return dct


def parse_sort_date(date_str: Optional[str]) -> Optional[date]:
    """
    Parse a potentially incomplete date string of the format YYYY-MM-DD and
    return a datetime.date object with conservative defaults for missing data.
    """
    if date_str is None:
        return None

    try:
        ymd = [int(e) for e in date_str.split("-") if e != ""]
    except ValueError:
        return None
    if len(ymd) < 1:
        return None
    if len(ymd) < 2:
        ymd.append(12)
    if len(ymd) < 3:
        ymd.append(28)

    try:
        return date(*(int(v) for v in ymd))
    except ValueError:
        return None


def get_nested(sequence: Dict, keys: Iterable):
    """
    Get the value from a nested dict/list data structure, returning None if one
    of the keys is invalid.
    """
    current = sequence
    for key in keys:
        try:
            current = current[key]
        except (KeyError, IndexError):
            return None

    return current


def get_isrcs(el):
    """
    Find the ISRCs of item and return them as list
    """
    isrcs = []
    for key, val in el.items():
        if key.endswith(".isrcs"):
            isrcs.extend(val)
        if key.endswith(".isrc"):
            isrcs.append(val)
    return isrcs
