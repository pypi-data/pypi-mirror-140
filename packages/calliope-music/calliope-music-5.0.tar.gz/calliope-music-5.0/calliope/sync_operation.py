# Calliope
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


import click

import sys


class SyncOperation:
    """Base class for operations that do page-based downloads of remote data.

    Designed for integration with click.ProgressBar class.

    """
    def prepare(self, page_size):
        raise NotImplementedError()

    def pages(self):
        raise NotImplementedError()

    def process_page(self, page):
        raise NotImplementedError()

    def run(self, enable_progressbar=True, progressbar_stream=sys.stderr,
            progressbar_label=None):
        pages = self.pages()
        if enable_progressbar and progressbar_stream.isatty():
            with click.progressbar(iter(pages),
                                length=len(pages),
                                file=progressbar_stream,
                                label=progressbar_label) as pages_verbose:
                for page in pages_verbose:
                    self.process_page(page)
        else:
            for page in pages:
                self.process_page(page)
