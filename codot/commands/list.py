"""A class for the 'list' command.

Copyright © 2017-2018 Garrett Powell <garrett@gpowell.net>

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
import re

from codot import ANSI_RED, ANSI_NORMAL, HOME_DIR
from codot.utils import contract_user, BoxTable
from codot.commandbase import Command
from codot.container import ProgramData


class ListCommand(Command):
    """Run the "list" command.

    Attributes:
        group: The "--group" option was given.
        data: Persistent program information such as config values.
    """
    def __init__(self, group=False) -> None:
        super().__init__()
        self.group = group
        self.data = ProgramData()

    def main(self) -> None:
        try:
            self.data.read()
        except FileNotFoundError:
            self.data.generate()

        # Compile regex for pulling identifier names from template files.
        identifier_regex = re.compile(
            re.escape(self.data.id_format).replace(
                r"\%s", r"([\w-]+)"))

        # Get a dict of identifiers from each template file.
        template_identifiers = {}
        for template in self.user_files.get_templates():
            source_path = contract_user(template.source_path)
            template_identifiers[source_path] = template.get_identifier_names(
                self.data.id_format)

        # Get a list of identifiers present in any config file.
        config_identifiers = self.user_files.get_config_values().keys()

        if not template_identifiers:
            print("\n-- No identifiers --\n")
            return

        def add_color(identifier: str) -> str:
            if identifier in config_identifiers:
                return identifier
            else:
                return ANSI_RED + identifier + ANSI_NORMAL

        # Construct data for the table.
        if self.group:
            table_data = [("Identifier", "Template File")]
            for source_path, identifiers in sorted(
                    template_identifiers.items()):
                identifiers.sort()
                table_data.append(("", ""))
                table_data.append((add_color(identifiers[0]), source_path))
                table_data.extend(
                    (add_color(identifier), "")
                    for identifier in identifiers[1:])

            # Remove the blank row at the top of the table.
            del table_data[1]
        else:
            unique_identifiers = {
                identifier for group in template_identifiers.values()
                for identifier in group}
            table_data = [("Identifier",)]
            table_data.extend(
                (add_color(identifier),)
                for identifier in sorted(unique_identifiers))

        # Print data as a table.
        table = BoxTable(table_data)
        print(table.format())
