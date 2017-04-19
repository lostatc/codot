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
import sys
import argparse
import pkg_resources
import textwrap

from codot.exceptions import InputError


def usage(command: str) -> None:
    """Print a usage message."""

    if sys.stdout.isatty():
        normal = chr(27) + "[0m"    # No formatting.
        strong = chr(27) + "[1m"    # Bold, used for commands/options.
        emphasis = chr(27) + "[4m"  # Underlined, used for arguments.
    else:
        # Don't use colors if stdout isn't a tty.
        normal = emphasis = strong = ""

    if not command:
        help_msg = textwrap.dedent("""\
            Usage: {1}codot{0} [{2}global_options{0}] {2}command{0} [{2}command_options{0}] [{2}command_args{0}]

            Global options:
                    {1}--help{0}          Print a usage message and exit.
                    {1}--version{0}       Print the version number and exit.
                {1}-q{0}, {1}--quiet{0}         Suppress all non-error output.

            Commands:
                {1}sync{0} [{2}options{0}] [{2}config_name{0}...]
                    Propogate changes in the config files given by {2}config_name{0} to all
                    source files for which there is a template file, but only if those
                    source files have not been modified since the last sync. If {2}config_name{0}
                    is not specified, then changes in all config files will be propogated.

                {1}role{0} {2}role_name{0} [{2}config_name{0}]
                    Switch the currently selected config file in the role named {2}role_name{0}.
                    If {2}config_name{0} is specified, that config file will be selected.
                    Otherwise, it will show a list of config files available for that role.
            """)
    elif command == "sync":
        help_msg = textwrap.dedent("""\
            {1}sync{0} [{2}options{0}] [{2}config_name{0}...]
                Propogate changes in the config files given by {2}config_name{0} to all source
                files for which there is a template file, but only if those source files
                have not been modified since the last sync. If {2}config_name{0} is not
                specified, then changes in all config files will be propogated.

                {1}-o{0}, {1}--overwrite{0}
                    Overwrite the source files even if they've been modified since the last
                    sync.
            """)
    elif command == "role":
        help_msg = textwrap.dedent("""\
            {1}role{0} {2}role_name{0} [{2}config_name{0}]
                Switch the currently selected config file in the role named {2}role_name{0}. If
                {2}config_name{0} is specified, that config file will be selected. Otherwise, it
                will show a list of config files available for that role.
            """)
    else:
        help_msg = ""

    help_msg = help_msg.format(normal, strong, emphasis)
    print(help_msg)


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
    parser.add_argument("--quiet", "-q", action=QuietAction)

    subparsers = parser.add_subparsers(dest="command")
    subparsers.required = True

    parser_sync = subparsers.add_parser("sync", add_help=False)
    parser_sync.add_argument("--help", action=HelpAction)
    parser_sync.add_argument("--overwrite", "-o", action="store_true")
    parser_sync.add_argument(
        "config_names", nargs="*", default=None, metavar="config names")
    parser_sync.set_defaults(command="sync")

    parser_role = subparsers.add_parser("role", add_help=False)
    parser_role.add_argument("--help", action=HelpAction)
    parser_role.add_argument("role_name", metavar="role name")
    parser_role.add_argument(
        "config_name", nargs="?", default=None, metavar="config name")
    parser_role.set_defaults(command="role")

    return parser.parse_args()
