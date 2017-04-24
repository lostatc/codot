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

from codot import CONFIG_DIR, CONFIG_EXT
from codot.exceptions import InputError
from codot.basecommand import Command


class RoleCommand(Command):
    """Switch the currently selected config file for a role.

    Attributes:
        role_name: The name of the role to modify.
        role_path: The absolute path of the role directory.
        config_name: The name of the config file to select for the role.
    """
    def __init__(self, role_name: str, config_name=None) -> None:
        super().__init__()
        self.role_name = role_name
        self.role_path = os.path.join(CONFIG_DIR, role_name)
        if config_name:
            if config_name.endswith(CONFIG_EXT):
                self.config_name = config_name
            else:
                self.config_name = config_name + CONFIG_EXT
        else:
            self.config_name = None

    def main(self) -> None:
        super().main()
        self.lock()
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
                if self.get_selected(self.role_name) == config_name:
                    print("> ", end="")
                else:
                    print("  ", end="")
                print(config_name.rsplit(CONFIG_EXT, 1)[0])
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
            self.role_name, self.config_name.rsplit(CONFIG_EXT, 1)[0]))
