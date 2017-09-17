"""A class for the 'add-template' command.

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
from typing import List

from codot import HOME_DIR, TEMPLATES_DIR
from codot.utils import open_text_editor
from codot.commandbase import Command


class AddTemplateCommand(Command):
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

        with tempfile.TemporaryDirectory(prefix="codot-") as tmp_dir_path:
            for source_path in self.files:
                template_path = os.path.join(
                    TEMPLATES_DIR, os.path.relpath(source_path, HOME_DIR))

                # This is not in a context manager because the file will be
                # cleaned up with the parent directory.
                tmp_file = tempfile.NamedTemporaryFile(
                    dir=tmp_dir_path, delete=False)
                tmp_file_path = tmp_file.name
                tmp_file.close()
                if os.path.isfile(template_path) and self.revise:
                    shutil.copy(template_path, tmp_file_path)
                else:
                    shutil.copy(source_path, tmp_file_path)

                return_code = open_text_editor(tmp_file_path)
                if return_code != 0:
                    continue
                os.makedirs(os.path.dirname(template_path), exist_ok=True)
                shutil.move(tmp_file_path, template_path)
