"""Integration tests for each command.

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
import sys
import builtins
import textwrap
from typing import NamedTuple

import pytest

import codot
from codot import (
    HOME_DIR, PROGRAM_DIR, CONFIG_DIR, TEMPLATES_DIR, PRIORITY_FILE,
    CONFIG_EXT)
from codot.exceptions import InputError
from codot.utils import rm_ext
from codot.commands.role import RoleCommand
from codot.commands.sync import SyncCommand
from codot.container import ProgramData

real_open = builtins.open

PathNameBase = NamedTuple("PathNameBase", [("path", str)])


class PathName(PathNameBase):
    __slots__ = ()

    @property
    def name(self) -> str:
        return rm_ext(os.path.basename(self.path), CONFIG_EXT)


FakeFilePaths = NamedTuple(
    "FakeFilePaths", [
        ("role", PathName), ("role_config1", PathName),
        ("role_config2", PathName), ("config", PathName),
        ("template", str), ("source", str)
    ])


@pytest.fixture
def copy_config(fs):
    """Copy the template config file to the fake filesystem."""
    config_path = os.path.join(
        os.path.dirname(codot.__file__), "../docs/config/settings.conf")
    with real_open(config_path) as real_file:
        fs.CreateFile(
            os.path.join(sys.prefix, "share/codot/settings.conf"),
            contents=real_file.read())


@pytest.fixture
def fake_files(fs, copy_config) -> FakeFilePaths:
    """Create fake files for testing, using different identifier formats."""
    files = FakeFilePaths(
        PathName(os.path.join(CONFIG_DIR, "color_scheme")),
        PathName(os.path.join(CONFIG_DIR, "color_scheme/solarized.conf")),
        PathName(os.path.join(CONFIG_DIR, "color_scheme/zenburn.conf")),
        PathName(os.path.join(CONFIG_DIR, "desktop.conf")),
        os.path.join(TEMPLATES_DIR, ".config/i3/config"),
        os.path.join(HOME_DIR, ".config/i3/config"))

    # Create config files.
    fs.CreateFile(
        files.role_config1.path, contents=textwrap.dedent("""\
            ForegroundColor=#93a1a1
            BackgroundColor=#002b36
            Font=NotoSans
            """))
    fs.CreateFile(
        files.role_config2.path, contents=textwrap.dedent("""\
            ForegroundColor=#ffffff
            BackgroundColor=#000000
            Font=Roboto
            """))
    fs.CreateFile(
        files.config.path, contents=textwrap.dedent("""\
            Font=DejaVuSans
            FontSize=12
            """))
    os.symlink(files.role_config1.path, files.role.path + CONFIG_EXT)

    # Create template files.
    fs.CreateFile(
        files.template, contents=textwrap.dedent("""\
            {{Font}}
            {{FontSize}}
            {{ForegroundColor}}
            {{BackgroundColor}}
            """))

    # Create source files.
    fs.CreateFile(files.source)

    # Create 'priority' file.
    with open(PRIORITY_FILE, "w") as file:
        file.write("\n".join([files.role.name, files.config.name]))

    return files


class TestRoleCommand:
    def test_no_role_specified(self):
        """Not specifying a role returns None."""
        cmd = RoleCommand(None, None)
        assert cmd.main() is None

    def test_no_config_specified(self, fake_files):
        """Not specifying a config returns None."""
        cmd = RoleCommand(fake_files.role.name, None)
        assert cmd.main() is None

    def test_role_nonexistent(self, fake_files):
        """Specifying a role that doesn't exist raises an exception."""
        cmd = RoleCommand("foo", None)
        with pytest.raises(InputError):
            cmd.main()

    def test_config_nonexistent(self, fake_files):
        """Specifying a config that doesn't exist raises an exception."""
        cmd = RoleCommand(fake_files.role.name, "foo")
        with pytest.raises(InputError):
            cmd.main()

    @pytest.mark.parametrize("extension", ["", CONFIG_EXT])
    def test_symlink_created(self, fs, fake_files, extension):
        """A symlink is created for the role."""
        config_name = fake_files.role_config2.name + extension

        cmd = RoleCommand(fake_files.role.name, config_name)
        cmd.main()

        symlink_path = fake_files.role.path + CONFIG_EXT
        assert os.path.islink(symlink_path)
        assert os.readlink(symlink_path) == fake_files.role_config2.path


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
        """Values can be propagated with different identifier formats."""
        identifiers = ["Font", "FontSize", "ForegroundColor", "BackgroundColor"]
        template_contents = "\n".join(
            id_format.replace("%s", identifier) for identifier in identifiers)

        with open(fake_files.template, "w") as file:
            file.write(template_contents)

        cmd = SyncCommand()
        monkeypatch.setattr(cmd.data, "read", cmd.data.generate)
        monkeypatch.setattr(cmd.data.__class__, "id_format", id_format)
        cmd.main()

        expected_content = textwrap.dedent("""\
            NotoSans
            12
            #93a1a1
            #002b36""")
        with open(fake_files.source, "r") as file:
            assert file.read() == expected_content
