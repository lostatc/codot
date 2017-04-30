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
from typing import Collection

from codot import (
    HOME_DIR, TEMPLATES_DIR, CONFIG_DIR, INFO_FILE, SETTINGS_FILE,
    PRIORITY_FILE, CONFIG_EXT)
from codot.exceptions import StatusError, InputError
from codot.util import rec_scan, rshave
from codot.container import ConfigFile, ProgramInfoFile, ProgramConfigFile
from codot.basecommand import Command


class SyncCommand(Command):
    """Propagate changes in the config files to the source files.

    Attributes:
        overwrite: Overwrite source files even if they've been modified since
            the last sync.
    """
    def __init__(self, overwrite=False) -> None:
        super().__init__()
        self.overwrite = overwrite
        self.info_file = ProgramInfoFile(INFO_FILE)
        self.cfg_file = ProgramConfigFile(SETTINGS_FILE)

    def main(self) -> None:
        super().main()
        self.lock()
        self.cfg_file.read()
        try:
            self.info_file.read()
        except FileNotFoundError:
            self.info_file.generate()

        if self.overwrite or self.cfg_file.vals["OverwriteAlways"]:
            overwrite_source = True
        else:
            overwrite_source = False

        # Get a list of tuples each containing a matching template and
        # source file.
        template_pairs = []
        for entry in rec_scan(TEMPLATES_DIR):
            if not entry.is_file(follow_symlinks=False):
                continue

            template_path = entry.path
            source_path = os.path.join(
                HOME_DIR, os.path.relpath(entry.path, TEMPLATES_DIR))
            try:
                if os.path.isdir(source_path):
                    raise StatusError(
                        "source file exists and is a directory: "
                        + source_path)
                source_mtime = os.stat(source_path).st_mtime
            except FileNotFoundError:
                source_mtime = 0

            if (source_mtime <= self.info_file.vals["LastSync"]
                    or overwrite_source):
                template_pairs.append((template_path, source_path))

        # Get a priority-ordered list of enabled configs and roles.
        with open(PRIORITY_FILE, "r") as file:
            config_priority = [
                rshave(line.strip(), CONFIG_EXT) + CONFIG_EXT
                for line in file if line.strip()]

        # Get a dict of values from all config files. Reverse the order of
        # the priority file so that values from higher-priority files
        # overwrite values from lower-priority ones.
        config_values = {}
        for config_name in reversed(config_priority):
            full_path = os.path.join(CONFIG_DIR, config_name)
            config_file = ConfigFile(full_path)
            config_file.read()
            config_values.update(config_file.raw_vals)

        identifier_regex = re.compile(
            re.escape(self.cfg_file.vals["IdentifierFormat"]).replace(
                r"\%s", r"([\w-]+)"))

        # Replace identifiers in template files with values from config files.
        tmp_paths = []
        tmp_dir = tempfile.TemporaryDirectory(prefix="codot-")
        input_errors = []
        for template_path, source_path in template_pairs:
            with contextlib.ExitStack() as stack:
                # Temporary files are used to make updating the source files
                # a somewhat atomic operation. A temporary directory is used so
                # that the temp files are all cleaned up on program exit
                # without having to keep them open.
                tmp_file = stack.enter_context(
                    tempfile.NamedTemporaryFile(
                        mode="w+", dir=tmp_dir.name, delete=False))
                template_file = stack.enter_context(
                    open(template_path, "r"))

                for line in template_file:
                    new_line = line
                    for identifier_name in identifier_regex.findall(line):
                        if identifier_name not in config_values.keys():
                            input_errors.append(
                                "the identifier '{}' ".format(identifier_name)
                                + "is not in any enabled config file")
                            continue
                        new_line = new_line.replace(
                            self.cfg_file.vals["IdentifierFormat"].replace(
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
        for file_tuple in zip(tmp_paths, template_pairs):
            tmp_path, (template_path, source_path) = file_tuple
            os.makedirs(os.path.dirname(source_path), exist_ok=True)
            shutil.move(tmp_path, source_path)

        # The sync is now complete. Update the time of the last sync in the
        # info file.
        self.info_file.vals["LastSync"] = time.time()
        self.info_file.write()
