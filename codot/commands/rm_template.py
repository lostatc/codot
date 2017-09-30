"""A class for the 'rm-template' command.

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
import shutil
import tempfile
import contextlib
from typing import List

from codot import HOME_DIR
from codot.utils import contract_user
from codot.exceptions import InputError
from codot.container import ProgramData
from codot.commandbase import Command
from codot.user_files import TemplateFile


class RmTemplateCommand(Command):
    """Run the "rm-template" command.

    Attributes:
        files: The "files" argument for the command.
        leave_options: The "--leave-options" options was given.
        data: Persistent program information such as config values.
    """
    def __init__(self, files: List[str], leave_options=False) -> None:
        super().__init__()
        self.files = files
        self.leave_options = leave_options
        self.data = ProgramData()

    def main(self) -> None:
        try:
            self.data.read()
        except FileNotFoundError:
            self.data.generate()

        for source_path in self.files:
            abs_source_path = os.path.abspath(source_path)
            template = TemplateFile(
                os.path.relpath(abs_source_path, HOME_DIR),
                self.user_files.templates_dir)

            # Remove the template file.
            try:
                os.remove(template.path)
            except FileNotFoundError:
                raise InputError(
                    "the source file '{0}' has no corresponding template "
                    "file".format(contract_user(template.source_path)))

            # Remove any empty parent directories.
            parent_dir = os.path.dirname(template.path)
            while True:
                try:
                    os.rmdir(parent_dir)
                    parent_dir = os.path.dirname(parent_dir)
                except OSError:
                    break

        if not self.leave_options:
            # Get a set of names of identifiers used in all template files.
            template_identifiers = set()
            for template in self.user_files.get_templates():
                template_identifiers.update(
                    template.get_identifier_names(self.data.id_format))

            # Remove unused options from config files.
            for config in self.user_files.get_configs(enter_roles=True):
                with contextlib.ExitStack() as stack:
                    tmp_file = stack.enter_context(
                        tempfile.NamedTemporaryFile(mode="w+"))
                    config_file = stack.enter_context(open(config.path))

                    for line in config_file:
                        try:
                            key, value = config.readline(line)
                            if key in template_identifiers:
                                tmp_file.write(line)
                        except TypeError:
                            tmp_file.write(line)

                    tmp_file.flush()
                    shutil.copy(tmp_file.name, config.path)
