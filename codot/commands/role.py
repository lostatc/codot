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

from codot.basecommand import Command


class RoleCommand(Command):
    """Switch the currently selected config file for a role.

    Attributes:
        role_name: The name of the role to modify.
        config_name: The name of the config file to select for the role.
    """
    def __init__(self, role_name: str, config_name=None) -> None:
        super().__init__()
        self.role_name = role_name
        self.config_name = config_name

    def main(self) -> None:
        pass
