"""The main module for the program.

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

import signal
import sys
import argparse

from codot.commands.role import RoleCommand
from codot.commands.sync import SyncCommand
from codot.exceptions import ProgramError
from codot.input import parse_args
from codot.basecommand import Command


def main() -> int:
    """Start the program."""
    try:
        # Exit properly on SIGTERM, SIGHUP or SIGINT.
        signal.signal(signal.SIGTERM, signal_exception_handler)
        signal.signal(signal.SIGHUP, signal_exception_handler)
        signal.signal(signal.SIGINT, signal_exception_handler)

        cmd_args = parse_args()
        command = def_command(cmd_args)
        command.main()
    except ProgramError as e:
        for message in e.args:
            print("Error: {}".format(message), file=sys.stderr)
        return 1
    return 0


def def_command(cmd_args) -> Command:
    if cmd_args.command == "sync":
        return SyncCommand(cmd_args.config_names, cmd_args.overwrite)
    elif cmd_args.command == "role":
        return RoleCommand(cmd_args.role_name, cmd_args.config_name)


def signal_exception_handler(signum: int, frame) -> None:
    """Raise an exception with error message for an interruption by signal."""
    raise ProgramError("program received " + signal.Signals(signum).name)


def signal_exit_handler(signum: int, frame) -> None:
    """Exit the program normally in response to an interruption by signal."""
    sys.exit(0)
