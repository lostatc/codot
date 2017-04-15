"""The main module for the client.

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
import abc
import socket

from codot.exceptions import StatusError


class Command(abc.ABC):
    """Base class for program commands."""
    def __init__(self) -> None:
        self._lock_socket = None

    @abc.abstractmethod
    def main(self) -> None:
        """Run the command."""

    def lock(self) -> None:
        """Lock the program if not already locked.

        This prevents multiple operations from running at the same time. The
        lock is released automatically whenever the program exits, even via
        SIGKILL.

        Raises:
            StatusError: The program is already locked for the current user.
        """
        self._lock_socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        try:
            self._lock_socket.bind("\0" + "codot-" + str(os.getuid()))
        except socket.error:
            raise StatusError(
                "another operation on this profile is already taking place")
