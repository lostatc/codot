"""Manage command-line input and the printing of usage messages.

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
import signal
import sys
import argparse
import pkg_resources
import textwrap

from codot.exceptions import InputError, ProgramError
from codot.basecommand import Command
from codot.daemon import Daemon
from codot.commands.role import RoleCommand
from codot.commands.sync import SyncCommand


def usage(command: str) -> None:
    """Print a usage message."""

    if sys.stdout.isatty():
        format_chars = [
            chr(27) + "[0m",    # No formatting.
            chr(27) + "[1m",    # Bold, used for commands/options.
            chr(27) + "[4m"     # Underlined, used for arguments.
            ]
    else:
        # Don't use colors if stdout isn't a tty.
        format_chars = ["", "", ""]

    # textwrap.wrap() can't be used here in leu of manual formatting because
    # it doesn't account for the terminal control codes. The text wrap
    # feature of your editor probably won't work either for the same reason.
    # When editing these messages, make sure to manually wrap the text to
    # 79 columns, not counting the in-code indentation or the replacement
    # fields (e.g. {1}).
    if not command:
        help_msg = textwrap.dedent("""\
            Usage: {1}codot{0} [{2}global_options{0}] {2}command{0} [{2}command_options{0}] [{2}command_args{0}]

            Global options:
                    {1}--help{0}          Print a usage message and exit.
                    {1}--version{0}       Print the version number and exit.
                    {1}--debug{0}         Print a full stack trace instead of an error message if an
                                        error occurs.
                {1}-q{0}, {1}--quiet{0}         Suppress all non-error output.

            Commands:
                {1}sync{0} [{2}options{0}]
                    Propogate changes in all config files and roles to all source files for
                    which there is a template file, but only if those source files have not
                    been modified since the last sync.

                {1}role{0} [{2}role_name{0} [{2}config_name{0}]]
                    Make {2}config_name{0} the currently selected config file in the role named
                    {2}role_name{0}. If {2}config_name{0} is not specified, print a list of config files
                    available for that role and show which one is currently selected. If
                    {2}role_name{0} is not specified, print a table of all roles and their
                    selected config files. 

            """)
    elif command == "sync":
        help_msg = textwrap.dedent("""\
            {1}sync{0} [{2}options{0}]
                Propogate changes in all config files and roles to all source files for
                which there is a template file, but only if those source files have not
                been modified since the last sync.

                {1}-o{0}, {1}--overwrite{0}
                    Overwrite the source files even if they've been modified since the last
                    sync.
            """)
    elif command == "role":
        help_msg = textwrap.dedent("""\
            {1}role{0} [{2}role_name{0} [{2}config_name{0}]]
                Make {2}config_name{0} the currently selected config file in the role named
                {2}role_name{0}. If {2}config_name{0} is not specified, print a list of config files
                available for that role and show which one is currently selected. If
                {2}role_name{0} is not specified, print a table of all roles and their selected
                config files. 
            """)
    else:
        help_msg = ""

    help_msg = help_msg.format(*format_chars)
    print(help_msg, end="")


class CustomArgumentParser(argparse.ArgumentParser):
    """Set custom formatting of error messages for argparse."""
    def error(self, message) -> None:
        raise InputError(message)


class HelpAction(argparse.Action):
    """Handle the '--help' flag."""
    def __init__(self, nargs=0, **kwargs) -> None:
        super().__init__(nargs=nargs, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None) -> None:
        usage(namespace.command)
        parser.exit()


class VersionAction(argparse.Action):
    """Handle the '--version' flag."""
    def __init__(self, nargs=0, **kwargs) -> None:
        super().__init__(nargs=nargs, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None) -> None:
        print(
            "codot",
            pkg_resources.get_distribution("codot").version)
        parser.exit()


class QuietAction(argparse.Action):
    """Handle the '--quiet' flag."""
    def __init__(self, nargs=0, **kwargs) -> None:
        super().__init__(nargs=nargs, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None) -> None:
        sys.stdout = open(os.devnull, "a")


def parse_args() -> argparse.Namespace:
    """Create a dictionary of parsed command-line arguments.

    Returns:
        A namespace of command-line argument names and their values.
    """

    parser = CustomArgumentParser(add_help=False)
    parser.add_argument("--help", action=HelpAction)
    parser.add_argument("--version", action=VersionAction)
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--quiet", "-q", action=QuietAction)

    subparsers = parser.add_subparsers(dest="command")
    subparsers.required = True

    parser_sync = subparsers.add_parser("sync", add_help=False)
    parser_sync.add_argument("--help", action=HelpAction)
    parser_sync.add_argument("--overwrite", "-o", action="store_true")
    parser_sync.set_defaults(command="sync")

    parser_role = subparsers.add_parser("role", add_help=False)
    parser_role.add_argument("--help", action=HelpAction)
    parser_role.add_argument(
        "role_name", nargs="?", default=None, metavar="role name")
    parser_role.add_argument(
        "config_name", nargs="?", default=None, metavar="config name")
    parser_role.set_defaults(command="role")

    return parser.parse_args()


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
    except ProgramError as error:
        try:
            if cmd_args.debug:
                raise
        except NameError:
            pass
        for message in error.args:
            print("Error: {}".format(message), file=sys.stderr)
        return 1
    return 0


def daemon() -> int:
    """Start the daemon.

    Always print a full stack trace instead of an error message.
    """
    # Exit properly on SIGTERM, SIGHUP or SIGINT. SIGTERM is the method
    # by which the daemon will normally exit, and should not raise an
    # exception.
    signal.signal(signal.SIGTERM, signal_exit_handler)
    signal.signal(signal.SIGHUP, signal_exception_handler)
    signal.signal(signal.SIGINT, signal_exception_handler)

    ghost = Daemon()
    ghost.main()
    return 0


def def_command(cmd_args) -> Command:
    if cmd_args.command == "sync":
        return SyncCommand(cmd_args.overwrite)
    elif cmd_args.command == "role":
        return RoleCommand(cmd_args.role_name, cmd_args.config_name)


def signal_exception_handler(signum: int, frame) -> None:
    """Raise an exception with error message for an interruption by signal."""
    raise ProgramError("program received " + signal.Signals(signum).name)


def signal_exit_handler(signum: int, frame) -> None:
    """Exit the program normally in response to an interruption by signal."""
    sys.exit(0)
