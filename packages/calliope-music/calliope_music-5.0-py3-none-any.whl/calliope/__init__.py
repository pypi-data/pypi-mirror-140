# Calliope
# Copyright (C) 2016,2018  Sam Thursfield <sam@afuera.me.uk>
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

'''Calliope is a set of tools for processing playlists.

This module contains the core parts of Calliope.

'''

import configparser
import importlib
import logging
import os

log = logging.getLogger(__name__)


class DisabledModule():
    """Helper to raise ImportError exceptions for disabled modules."""
    def __init__(self, name):
        self.name = name

    def __getattr__(self, attr):
        raise RuntimeError(f"Module {self.name} was disabled at configure time.")


class FailedModule:
    """Helper to defer ImportError exceptions until module is actually used."""
    def __init__(self, name, error):
        self.name = name
        self.error = error

    def __getattr__(self, attr):
        raise self.error

    def runtime_error(self, command_name=None):
        """Return an error appropriate for display in CLI."""
        command_name = command_name or self.name
        return RuntimeError('\n'.join([
            f"Command '{command_name}' is not available.",
            "",
            "You can install this module's dependencies using `pip`, for example:",
            "",
            f"    pip install calliope-music[{self.name}]",
            "",
            f"Original error: {self.error}"]))

    def runtime_error_gobject_introspection(self, command_name=None):
        command_name = command_name or self.name
        return RuntimeError('\n'.join([
            f"Command '{command_name}' is not available.",
            "",
            "This module requires system dependencies that are accessed via PyGObject.",
            "Consult your distribution documentation for how to install GObject Introspection ",
            "bindings and PyGObject.",
            "",
            f"Original error: {self.error}"]))


class ModuleLoader:
    """Wrapper module import to avoid requiring all dependencies at import time.

    We want `import calliope` to import the whole Calliope library. However,
    this pulls in a lot of dependencies by default. This helper class allows
    features to be disabled at runtime (used in PyPI installs), or at configure
    time (used in Meson installs).
    """
    def __init__(self):
        self.config = None

    def load_config(self):
        if 'CALLIOPE_MODULES_CONFIG' in os.environ:
            modules_config_file = os.environ['CALLIOPE_MODULES_CONFIG']
        else:
            module_path = os.path.dirname(__file__)
            modules_config_file = os.path.join(module_path, 'modules.conf')

        if os.path.exists(modules_config_file):
            config = configparser.ConfigParser()
            config.read(modules_config_file)
            self.config = config

    def maybe_load_module(self, name):
        if self.config:
            if self.config.get('Modules', name) == 'True':
                log.debug("Module %s enabled by config, loading and raising any errors", name)
                return importlib.import_module('.' + name, 'calliope')
            else:
                log.debug("Module %s disabled by config", name)
                return DisabledModule(name)
        else:
            log.debug("Trying to load %s", name)
            try:
                return importlib.import_module('.' + name, 'calliope')
            except (ImportError, ModuleNotFoundError) as e:
                # This code runs during initial module import so the log
                # message is unlikely to be seen
                log.debug("Failed to import %s: %s", name, e)
                return FailedModule(name, e)


if os.environ.get('CALLIOPE_DOCS_BUILD') == 'yes':
    # When building the documentation, we stub out everything apart from the
    # Click CLI functions. This allows Sphinx plugins to run `import calliope`
    # without needing to have all of the dependencies available. We do this so
    # that we can use online documentation hosting at readthedocs.org.
    from . import cli
else:
    import json
    import pathlib
    import urllib.parse


    def uri_to_path(uri):
        '''Convert a file:/// URI to a pathlib.Path.'''
        return pathlib.Path(urllib.parse.unquote(
            urllib.parse.urlsplit(uri).path))


    from . import cache
    from . import cli
    from . import config
    from . import playlist

    from . import beets
    from . import diff
    from . import export
    from . import import_
    from . import shuffle
    from . import stat
    from . import sync
    from . import validate


    loader = ModuleLoader()
    loader.load_config()

    # These modules may fail due to missing dependencies.
    #
    # By default, a FailedModule object is returned which overrides
    # __getattr__() to show the import error to the user.
    #
    # The rationale is: we don't want to fail unless the module is actually
    # used, as that would break every other module and the CLI.
    bandcamp = loader.maybe_load_module('bandcamp')
    lastfm = loader.maybe_load_module('lastfm')
    listenbrainz = loader.maybe_load_module('listenbrainz')
    musicbrainz = loader.maybe_load_module('musicbrainz')
    play = loader.maybe_load_module('play')
    select = loader.maybe_load_module('select')
    spotify = loader.maybe_load_module('spotify')
    suggest = loader.maybe_load_module('suggest')
    tracker = loader.maybe_load_module('tracker')
    youtube = loader.maybe_load_module('youtube')
