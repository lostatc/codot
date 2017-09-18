"""A class for the 'list' command.

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
import re

from terminaltables import SingleTable

from codot import TEMPLATES_DIR, CONFIG_DIR, ANSI_RED, ANSI_NORMAL, CONFIG_EXT
from codot.utils import rec_scan
from codot.commandbase import Command
from codot.container import ProgramData, ConfigFile


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
        # Compile regex for pulling identifier names from template files.
        identifier_regex = re.compile(
            re.escape(self.data.id_format).replace(
                r"\%s", r"([\w-]+)"))

        # Get a dict of identifiers from each template file.
        template_identifiers = {}
        for entry in rec_scan(TEMPLATES_DIR):
            if not entry.is_file():
                continue

            source_path = os.path.join(
                "~", os.path.relpath(entry.path, TEMPLATES_DIR))
            template_identifiers[source_path] = []

            with open(entry.path) as file:
                for line in file:
                    for match_string in identifier_regex.findall(line):
                        template_identifiers[source_path].append(match_string)

        # Get a list of identifiers present in any config file.
        config_identifiers = []
        for entry in rec_scan(CONFIG_DIR):
            if not entry.name.endswith(CONFIG_EXT):
                continue
            config_file = ConfigFile(entry.path)
            config_file.read()
            config_identifiers.extend(config_file.raw_vals.keys())

        # Construct data for the table.
        if self.group:
            table_data = [("Identifiers", "Template File")]
        else:
            table_data = [("Identifiers",)]
            used_identifiers = set()

        for source_path, identifiers in sorted(
                template_identifiers.items(), key=lambda x: x[0]):
            for i, identifier in enumerate(sorted(identifiers)):
                if identifier in config_identifiers:
                    identifier_entry = identifier
                else:
                    identifier_entry = ANSI_RED + identifier + ANSI_NORMAL

                if i == 0:
                    source_path_entry = source_path
                else:
                    source_path_entry = ""

                if self.group:
                    table_data.append((identifier_entry, source_path_entry))
                else:
                    if identifier in used_identifiers:
                        continue
                    table_data.append((identifier_entry,))
                    used_identifiers.add(identifier)

        # Print data as a table.
        table = SingleTable(table_data)
        print(table.table)
