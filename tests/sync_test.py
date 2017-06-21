"""Test the 'sync' command.

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
import textwrap

import pytest

from tests.base import fake_files, copy_config
from codot import HOME_DIR, INFO_FILE, PRIORITY_FILE, CONFIG_EXT
from codot.exceptions import InputError
from codot.commands.sync import SyncCommand
from codot.utils import rclip
from codot.container import ProgramData


class TestSyncCommand:
    @pytest.mark.parametrize("overwrite", [True, False])
    def test_overwrite_source_files(self, fs, fake_files, overwrite):
        """Modified source files are ignored unless otherwise specified."""
        # Set mtime of source file to be more recent than the time of the last
        # sync in the info file.
        data = ProgramData()
        data.generate()
        os.utime(fake_files.source, times=None)

        cmd = SyncCommand(overwrite=overwrite)
        cmd.main()

        if overwrite:
            assert os.stat(fake_files.source).st_size > 0
        else:
            assert os.stat(fake_files.source).st_size == 0

    def test_missing_identifiers(self, fs, fake_files):
        """Identifiers not found in a config file raise an exception."""
        with open(PRIORITY_FILE, "w") as file:
            file.write(fake_files.config.name)

        cmd = SyncCommand()
        with pytest.raises(InputError):
            cmd.main()

    def test_missing_source_files(self, fs, fake_files):
        """Template files without corresponding source files are ignored."""
        os.remove(fake_files.source)

        cmd = SyncCommand()
        cmd.main()

        assert not os.path.isfile(fake_files.source)

    @pytest.mark.parametrize("id_format", ["{{%s}}", "__%s__", "${%s}"])
    def test_propagate_config_changes(
            self, fake_files, monkeypatch, id_format):
        """Values propagated with different identifier formats."""
        identifiers = ["Font", "FontSize", "ForegroundColor", "BackgroundColor"]
        template_contents = "\n".join(
            id_format.replace("%s", identifier) for identifier in identifiers)

        with open(fake_files.template, "w") as file:
            file.write(template_contents)

        cmd = SyncCommand()
        monkeypatch.setattr(cmd.data, "read", cmd.data.generate)
        monkeypatch.setattr(cmd.data, "id_format", id_format)
        cmd.main()

        expected_content = textwrap.dedent("""\
            NotoSans
            12
            #93a1a1
            #002b36""")
        with open(fake_files.source, "r") as file:
            assert file.read() == expected_content
