"""A class for the 'init' command.

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
import os
import sys
import shutil

from codot import (
    PROGRAM_DIR, TEMPLATES_DIR, CONFIG_DIR, PRIORITY_FILE, SETTINGS_FILE)
from codot.commandbase import Command


class InitCommand(Command):
    """Generate the program directory and all its files.

    This command is necessary so that the user can start editing files
    in the program directory without having to run another command first.
    """
    def main(self):
        """Run the command."""
        os.makedirs(PROGRAM_DIR, exist_ok=True)
        os.makedirs(TEMPLATES_DIR, exist_ok=True)
        os.makedirs(CONFIG_DIR, exist_ok=True)
        open(PRIORITY_FILE, "a").close()
        if not os.path.isfile(SETTINGS_FILE):
            # TODO: Get this path from setup.py instead of hardcoding it.
            shutil.copy(
                os.path.join(sys.prefix, "share/codot/settings.conf"),
                SETTINGS_FILE)
