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

from codot import CONFIG_DIR, CONFIG_EXT, InputError
from codot.basecommand import Command
from codot.utils import print_table, rclip


class RoleCommand(Command):
    """Switch the currently selected config file for a role.

    Attributes:
        role_name: The name of the role to modify.
        role_path: The absolute path of the role directory.
        config_name: The name of the config file to select for the role.
    """
    def __init__(
            self, role_name: Optional[str], config_name=Optional[str]) -> None:
        super().__init__()
        self.role_name = role_name
        self.role_path = os.path.join(
            CONFIG_DIR, role_name) if role_name else None
        self.config_name = rclip(
            config_name, CONFIG_EXT) + CONFIG_EXT if config_name else None

    def main(self) -> None:
        super().main()
        self.lock()

        if not self.role_name:
            role_names = []
            for entry in os.scandir(CONFIG_DIR):
                if not entry.is_dir():
                    continue
                role_name = entry.name
                try:
                    selected_config = os.path.basename(rclip(
                        os.readlink(entry.path + CONFIG_EXT), CONFIG_EXT))
                except FileNotFoundError:
                    selected_config = ""
                role_names.append((role_name, selected_config))
            role_names.sort(key=lambda x: x[1])
            headers = ["Role", "Selected Config"]
            print_table(headers, role_names)
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
                        + chr(27) + "[32m"
                        + rclip(config_name, CONFIG_EXT)
                        + chr(27) + "[0m")
                else:
                    print_output = "  " + rclip(config_name, CONFIG_EXT)
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
            self.role_name, rclip(self.config_name, CONFIG_EXT)))
