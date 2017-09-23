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
from codot import ANSI_NORMAL, ANSI_GREEN
from codot.exceptions import InputError
from codot.commandbase import Command
from codot.user_files import Role


class RoleCommand(Command):
    """Run the "role" command.

    Attributes:
        role_name: The "role_name" argument for the command.
        config_name: The "config_name" argument for the command.
        role: A Role object for the role.
        config: A UserConfigFile object for the role.
    """
    def __init__(
            self, role_name: Optional[str], config_name: Optional[str]
            ) -> None:
        super().__init__()
        self.role_name = role_name
        self.config_name = config_name
        self.role = None
        self.config = None

    def main(self) -> None:
        self.lock()

        if not self.role_name:
            table_data = [
                (role.name, role.selected.name)
                for role in self.user_files.get_roles()]
            table_data.insert(0, ("Role", "Selected Config"))
            table = SingleTable(table_data)
            print(table.table)
            return

        self.role = Role(self.role_name, self.user_files.config_dir)

        if not os.path.isdir(self.role.dir_path):
            # Role directory doesn't exist.
            raise InputError("no such role '{}'".format(self.role_name))

        role_configs = self.role.get_configs()

        if not self.config_name:
            # List the names of available config files alphabetically,
            # indicating which one is selected.
            for config in sorted(role_configs, key=lambda x: x.name):
                print_output = []
                if self.role.selected.name == config.name:
                    print_output.append(
                        "* " + ANSI_GREEN + config.name + ANSI_NORMAL)
                else:
                    print_output.append("  " + config.name)
                print("\n".join(print_output))
            return

        # Get the selected config by its name if it exists.
        self.config = self.role.get_config_by_name(self.config_name)

        if not self.config:
            raise InputError(
                "no such config '{}' in this role".format(self.config_name))

        # Switch the selected config file.
        try:
            os.remove(self.role.symlink_path)
        except FileNotFoundError:
            pass
        os.symlink(self.config.path, self.role.symlink_path)
        print("Switched '{0}' to '{1}'".format(
            self.role_name, self.config.name))
