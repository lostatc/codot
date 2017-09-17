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

from linotype import DefinitionStyle, Formatter, Item

from codot.exceptions import InputError, ProgramError
from codot.commandbase import Command
from codot.daemon import Daemon
from codot.commands.template import TemplateCommand
from codot.commands.sync import SyncCommand
from codot.commands.role import RoleCommand


def help_item() -> Item:
    """Structure the help message.

    Returns:
        An Item object with the message.
    """
    formatter = Formatter()
    root_item = Item(formatter)

    usage = root_item.add_text("Usage:", item_id="usage")
    usage.add_definition(
        "codot", "[global_options] command [command_options] [command_args]",
        "")
    usage.add_text("\n")

    global_opts = root_item.add_text("Global Options:", item_id="global_opts")
    global_opts.formatter.definition_style = DefinitionStyle.ALIGNED
    global_opts.add_definition(
        "    --help", "",
        "Print a usage message and exit.")
    global_opts.add_definition(
        "    --version", "",
        "Print the version number and exit.")
    global_opts.add_definition(
        "    --debug", "",
        "Print a full stack trace instead of an error message if an error "
        "occurs.")
    global_opts.add_definition(
        "-q, --quiet", "",
        "Suppress all non-error output.")
    global_opts.add_text("\n")

    commands = root_item.add_text("Commands:", item_id="commands")

    template_cmd = commands.add_definition(
        "template", "[options] files...",
        "Open one or more source files in your editor and save them each as "
        "a template file.", item_id="template")
    template_cmd.add_text("\n")
    template_cmd.add_definition(
        "-r, --revise", "",
        "If the template file already exists, edit it instead of creating a "
        "new one.")
    commands.add_text("\n")

    sync_cmd = commands.add_definition(
        "sync", "[options]",
        "Update source files with changes from config files, but only if "
        "those source files have not been modified since the last sync.",
        item_id="sync")
    sync_cmd.add_text("\n")
    sync_cmd.add_definition(
        "-o, --overwrite", "",
        "Overwrite the source files even if they've been modified since the "
        "last sync.")
    commands.add_text("\n")

    role_cmd = commands.add_definition(
        "role", "[role_name [config_name]]",
        "Make config_name the currently selected config file in the role "
        "named role_name. If config_name is not specified, print a list of "
        "config files available for that role. If role_name is not "
        "specified, print a table of all roles.", item_id="role")

    return root_item


def help_message(command: str) -> str:
    """Get the help message.

    Args:
        command: The command to print the help message of. If 'None,' print the
            general help message.

    Returns:
        The help message as a string.
    """
    if command:
        return help_item().format(item_id=command)
    else:
        return help_item().format(levels=2)


class CustomArgumentParser(argparse.ArgumentParser):
    """Set custom formatting of error messages for argparse."""
    def error(self, message) -> None:
        raise InputError(message)


class HelpAction(argparse.Action):
    """Handle the '--help' flag."""
    def __init__(self, nargs=0, **kwargs) -> None:
        super().__init__(nargs=nargs, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None) -> None:
        print(help_message(namespace.command))
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

    parser_template = subparsers.add_parser("template", add_help=False)
    parser_template.add_argument("--help", action=HelpAction)
    parser_template.add_argument("--revise", "-r", action="store_true")
    parser_template.add_argument(
        "files", nargs="+", metavar="files")
    parser_template.set_defaults(command="template")

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
    if cmd_args.command == "template":
        return TemplateCommand(cmd_args.files, cmd_args.revise)
    elif cmd_args.command == "sync":
        return SyncCommand(cmd_args.overwrite)
    elif cmd_args.command == "role":
        return RoleCommand(cmd_args.role_name, cmd_args.config_name)


def signal_exception_handler(signum: int, frame) -> None:
    """Raise an exception with error message for an interruption by signal."""
    raise ProgramError("program received " + signal.Signals(signum).name)


def signal_exit_handler(signum: int, frame) -> None:
    """Exit the program normally in response to an interruption by signal."""
    sys.exit(0)
