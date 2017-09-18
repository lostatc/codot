"""A class for the 'role' command.

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
from typing import Optional

from terminaltables import SingleTable
from codot import CONFIG_DIR, CONFIG_EXT, ANSI_NORMAL, ANSI_GREEN
from codot.exceptions import InputError
from codot.commandbase import Command
from codot.utils import rm_ext, add_ext


class RoleCommand(Command):
    """Run the "role" command.

    Attributes:
        role_name: The "role_name" argument for the command.
        config_name: The "config_name" argument for the command.
        role_path: The absolute path of the role directory.
    """
    def __init__(
            self, role_name: Optional[str], config_name: Optional[str]
            ) -> None:
        super().__init__()
        self.role_name = role_name
        self.role_path = os.path.join(
            CONFIG_DIR, role_name) if role_name else None
        self.config_name = add_ext(
            config_name, CONFIG_EXT) if config_name else None

    def main(self) -> None:
        self.lock()

        if not self.role_name:
            table_data = []
            for entry in os.scandir(CONFIG_DIR):
                if not entry.is_dir():
                    continue
                role_name = entry.name
                try:
                    selected_config = os.path.basename(rm_ext(
                        os.readlink(add_ext(entry.path, CONFIG_EXT)),
                        CONFIG_EXT))
                except FileNotFoundError:
                    selected_config = ""
                table_data.append((role_name, selected_config))
            table_data.sort(key=lambda x: x[1])
            table_data.insert(0, ("Role", "Selected Config"))
            table = SingleTable(table_data)
            print(table.table)
            return

        if not os.path.isdir(self.role_path):
            # Role directory doesn't exist.
            raise InputError("no such role '{}'".format(self.role_name))

        # Get a list of the names of all available config files.
        role_configs = {
            entry.name for entry in os.scandir(self.role_path)
            if entry.is_file() and entry.name.endswith(CONFIG_EXT)}

        if not self.config_name:
            # List the names of available config files alphabetically,
            # indicating which one is selected.
            for config_name in sorted(role_configs):
                try:
                    selected_name = os.path.basename(
                        os.readlink(self.role_path + CONFIG_EXT))
                except FileNotFoundError:
                    selected_name = None
                if selected_name == config_name:
                    print_output = (
                        "* "
                        + ANSI_GREEN
                        + rm_ext(config_name, CONFIG_EXT)
                        + ANSI_NORMAL)
                else:
                    print_output = "  " + rm_ext(config_name, CONFIG_EXT)
                print(print_output)
            return

        # Switch selected config file.
        if self.config_name not in role_configs:
            raise InputError(
                "no such config '{}' in this role".format(self.config_name))
        try:
            os.remove(self.role_path + CONFIG_EXT)
        except FileNotFoundError:
            pass
        os.symlink(
            os.path.join(self.role_path, self.config_name),
            self.role_path + CONFIG_EXT)
        print("Switched '{0}' to '{1}'".format(
            self.role_name, rm_ext(self.config_name, CONFIG_EXT)))
