"""Watch for file modifications in config directory and initiate syncs.

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
import subprocess

import pyinotify

from codot import (
    HOME_DIR, CONFIG_DIR, TEMPLATES_DIR, PROGRAM_DIR, INFO_FILE, SETTINGS_FILE,
    PRIORITY_FILE, CONFIG_EXT)


class Daemon:
    """Watch for file modifications in config directory and initiate syncs.

    Every time a config file is modified, start a sync as a subprocess.

    Attributes:
        wm: The pyinotify watch manager.
    """
    def __init__(self) -> None:
        self.wm = pyinotify.WatchManager()

    def main(self) -> None:
        """Start the daemon."""
        mask = pyinotify.IN_CLOSE_WRITE | pyinotify.IN_CREATE
        notifier = pyinotify.Notifier(self.wm, self._sync, read_freq=1)
        notifier.coalesce_events()
        self.wm.add_watch(CONFIG_DIR, mask, rec=True, auto_add=True)
        self.wm.add_watch(TEMPLATES_DIR, mask, rec=True, auto_add=True)
        self.wm.add_watch(PROGRAM_DIR, mask, auto_add=True)

        notifier.loop()

    def _sync(self, event) -> None:
        """Initiate a sync in a subprocess."""
        # IN_CLOSE_WRITE will always fire with IN_CREATE, so ignore IN_CREATE.
        if not event.dir and event.maskname == "IN_CLOSE_WRITE":
            watch_path = self.wm.get_path(event.wd)
            valid_file = False
            if os.path.commonpath([
                    watch_path, TEMPLATES_DIR]) == TEMPLATES_DIR:
                # File is under the templates directory.
                source_path = os.path.join(
                    HOME_DIR, os.path.relpath(event.pathname, TEMPLATES_DIR))
                if os.path.isfile(source_path):
                    # The corresponding source file exists.
                    valid_file = True
            elif (os.path.commonpath([
                    watch_path, CONFIG_DIR]) == CONFIG_DIR
                    and event.name.endswith(CONFIG_EXT)):
                # File is under the config directory and has the proper
                # extension.
                valid_file = True
            elif event.pathname == PRIORITY_FILE:
                # File is the priority file.
                valid_file = True

            if valid_file:
                cmd = subprocess.Popen(
                    ["codot", "--debug", "sync"], bufsize=1,
                    stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE, universal_newlines=True)

                # Print the subprocess's stderr to stderr so that it is
                # added to the journal.
                for line in cmd.stderr:
                    if line:
                        print(line, file=sys.stderr, end="")
                cmd.wait()
                sys.stderr.flush()
