"""A class for the 'template' command.

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
import subprocess
from typing import List

from codot import HOME_DIR, TEMPLATES_DIR
from codot.commandbase import Command


class TemplateCommand(Command):
    """Create a template file from a source file.

    Attributes:
        revise: If the template file already exists, edit it instead of
            creating a new one.
    """
    def __init__(self, files: List[str], revise=False) -> None:
        super().__init__()
        self.files = files
        self.revise = revise

    def main(self) -> None:
        self.lock()

        # Get default editor for the platform. On Windows, executing the
        # text file directly invokes the default editor.
        if os.name == "nt":
            edit_command = ""
        elif os.name == "posix":
            unix_editors = [
                os.getenv("VISUAL"), os.getenv("EDITOR"), "nano", "vi"]
            edit_command = [
                editor for editor in unix_editors if editor is not None][0]
        else:
            raise OSError("unsupported platform")

        with tempfile.TemporaryDirectory(prefix="codot-") as tmp_dir_path:
            for source_path in self.files:
                template_path = os.path.join(
                    TEMPLATES_DIR, os.path.relpath(source_path, HOME_DIR))

                if os.path.isfile(template_path) and self.revise:
                    tmp_file_path = shutil.copy(template_path, tmp_dir_path)
                else:
                    tmp_file_path = shutil.copy(source_path, tmp_dir_path)

                edit_process = subprocess.run([edit_command, tmp_file_path])
                if edit_process.returncode != 0:
                    continue
                os.makedirs(os.path.dirname(template_path), exist_ok=True)
                shutil.move(tmp_file_path, template_path)
