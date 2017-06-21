"""Fixtures for all testing modules.

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
from codot.utils import rclip

real_open = builtins.open

PathNameBase = NamedTuple("PathNameBase", [("path", str)])


class PathName(PathNameBase):
    __slots__ = ()

    @property
    def name(self) -> str:
        return rclip(os.path.basename(self.path), CONFIG_EXT)


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
