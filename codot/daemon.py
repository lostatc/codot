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

from codot.commandbase import Command


class Daemon(Command):
    """Watch for file modifications in config directory and initiate syncs.

    Every time a config file is modified, start a sync as a subprocess.

    Attributes:
        wm: The pyinotify watch manager.
    """
    def __init__(self) -> None:
        super().__init__()
        self.wm = pyinotify.WatchManager()

    def main(self) -> None:
        """Start the daemon."""
        mask = pyinotify.IN_CLOSE_WRITE | pyinotify.IN_CREATE
        notifier = pyinotify.Notifier(self.wm, self._check_event, read_freq=1)
        notifier.coalesce_events()
        self.wm.add_watch(
            self.user_files.config_dir, mask, rec=True, auto_add=True)
        self.wm.add_watch(
            self.user_files.templates_dir, mask, rec=True, auto_add=True)

        self._sync()
        notifier.loop()

    def _check_event(self, event) -> None:
        """Conditionally initiate a sync based on the event."""
        if not event.dir and event.maskname == "IN_CLOSE_WRITE":
            template_paths = {
                template.path for template in self.user_files.get_templates()}
            config_paths = {
                config.path for config in self.user_files.get_configs(
                    enter_roles=True)}

            if event.pathname in template_paths | config_paths:
                self._sync()

    @staticmethod
    def _sync() -> None:
        """Initiate a sync in a subprocess."""
        cmd = subprocess.Popen(
            ["codot", "--debug", "sync"], bufsize=1,
            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, universal_newlines=True)

        # Print the subprocess's stderr to stderr so that it is added to the
        # journal.
        for line in cmd.stderr:
            if line:
                print(line, file=sys.stderr, end="")
        cmd.wait()
        sys.stderr.flush()
