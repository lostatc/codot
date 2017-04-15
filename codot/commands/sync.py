"""A class for the 'sync' command.

Copyright © 2017 Garrett Powell <garrett@gpowell.net>

This file is part of codot.

codot is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

codot is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with codot.  If not, see <http://www.gnu.org/licenses/>.
"""

from typing import Collection

from codot.basecommand import Command


class SyncCommand(Command):
    """Propagate changes in the config files to the source files.

    Attributes:
        config_names: A collection of the names of config files to propagate
            the changes of.
        overwrite: Overwrite source files even if they've been modified since
            the last sync.
    """
    def __init__(self, config_names: Collection, overwrite=False) -> None:
        super().__init__()
        self.config_names = config_names
        self.overwrite = overwrite

    def main(self) -> None:
        pass
