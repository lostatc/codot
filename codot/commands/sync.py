"""A class for the 'sync' command.

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
import time
import tempfile
import shutil
import re
import contextlib

from codot.exceptions import InputError
from codot.utils import contract_user
from codot.container import ProgramData
from codot.commandbase import Command


class SyncCommand(Command):
    """Run the "sync" command.

    Attributes:
        overwrite: The "--overwrite" option was given.
        data: Persistent program information such as config values.
    """
    def __init__(self, overwrite=False) -> None:
        super().__init__()
        self.overwrite = overwrite
        self.data = ProgramData()

    def main(self) -> None:
        self.lock()
        try:
            self.data.read()
        except FileNotFoundError:
            self.data.generate()

        overwrite_source = bool(self.overwrite or self.data.overwrite_always)

        # Get a list of templates, possibly excluding templates that have been
        # modified since the last sync.
        templates = []
        ignored_templates = []
        for template in self.user_files.get_templates():
            source_mtime = os.stat(template.source_path).st_mtime
            if source_mtime <= self.data.last_sync or overwrite_source:
                templates.append(template)
            else:
                ignored_templates.append(template)

        config_values = self.user_files.get_config_values()

        identifier_regex = re.compile(
            re.escape(self.data.id_format).replace(
                r"\%s", r"([\w-]+)"))

        # Replace identifiers in template files with values from config files.
        tmp_paths = []
        tmp_dir = tempfile.TemporaryDirectory(prefix="codot-")
        input_errors = []
        for template in templates:
            with contextlib.ExitStack() as stack:
                # Temporary files are used to make updating the source files
                # a somewhat atomic operation. A temporary directory is used so
                # that the temp files are all cleaned up on program exit
                # without having to keep them open.
                tmp_file = stack.enter_context(
                    tempfile.NamedTemporaryFile(
                        mode="w+", dir=tmp_dir.name, delete=False))
                template_file = stack.enter_context(
                    open(template.path, "r"))

                for line in template_file:
                    new_line = line
                    for identifier_name in identifier_regex.findall(line):
                        if identifier_name not in config_values.keys():
                            input_errors.append(
                                "the identifier '{}' ".format(identifier_name)
                                + "is not in any enabled config file")
                            continue
                        new_line = new_line.replace(
                            self.data.id_format.replace(
                                "%s", identifier_name),
                            config_values[identifier_name])
                    tmp_file.write(new_line)

            # Only overwrite source files once all template files have been
            # checked for recognized identifiers.
            tmp_paths.append(tmp_file.name)

        # There were identifiers in one or more template files that are
        # not in any config files.
        if input_errors:
            raise InputError(*input_errors)

        # Overwrite source files with updated template files.
        for tmp_path, template in zip(tmp_paths, templates):
            os.makedirs(os.path.dirname(template.source_path), exist_ok=True)
            shutil.move(tmp_path, template.source_path)

        # Print a list of updated and skipped source paths.
        updated_output = [
            "Updated {}".format(contract_user(template.source_path))
            for template in templates]
        ignored_output = [
            "Skipped {}".format(contract_user(template.source_path))
            for template in ignored_templates]
        print("\n".join(updated_output + ignored_output))

        # The sync is now complete. Update the time of the last sync in the
        # info file.
        self.data.last_sync = time.time()
        self.data.write()
