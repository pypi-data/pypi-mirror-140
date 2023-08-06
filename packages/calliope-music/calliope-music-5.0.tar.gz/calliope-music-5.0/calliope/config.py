# Calliope
# Copyright (C) 2017  Sam Thursfield <sam@afuera.me.uk>
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


import configparser
import logging
import os
import pathlib

log = logging.getLogger(__name__)


def xdg_config_dirs():
    # Code taken from pyxdg module.
    #
    # We avoid using xdg.BaseDirectory here because it reads the environment
    # only on startup and then stores the directories as globals. We want to
    # honour changes in the environment after the start of the process so
    # that click.testing.CliRunner can manage them.
    _home = os.path.expanduser('~')
    xdg_config_home = os.environ.get('XDG_CONFIG_HOME') or \
            os.path.join(_home, '.config')
    return [xdg_config_home] + \
        (os.environ.get('XDG_CONFIG_DIRS') or '/etc/xdg').split(':')


class Configuration():
    def __init__(self):
        self.parser = configparser.ConfigParser()
        for config_dir in xdg_config_dirs():
            config_file = pathlib.Path(config_dir).joinpath('calliope/calliope.conf')
            if config_file.exists():
                log.debug("Reading config from %s", config_file)
                self.parser.read(config_file)

    def get(self, section, value):
        try:
            return self.parser.get(section, value)
        except (configparser.NoSectionError, configparser.NoOptionError):
            return None
