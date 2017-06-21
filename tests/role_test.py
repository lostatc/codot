"""Test the 'role' command.

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

import pytest

from tests.base import fake_files, copy_config
import codot
from codot import CONFIG_DIR, CONFIG_EXT
from codot.exceptions import InputError
from codot.utils import rclip
from codot.commands.role import RoleCommand


def test_no_role_specified():
    """Not specifying a role returns None."""
    cmd = RoleCommand(None, None)
    assert cmd.main() is None


def test_no_config_specified(fake_files):
    """Not specifying a config returns None."""
    cmd = RoleCommand(fake_files.role.name, None)
    assert cmd.main() is None


def test_role_nonexistent(fake_files):
    """Specifying a role that doesn't exist raises an exception."""
    cmd = RoleCommand("foo", None)
    with pytest.raises(InputError):
        cmd.main()


def test_config_nonexistent(fake_files):
    """Specifying a config that doesn't exist raises an exception."""
    cmd = RoleCommand(fake_files.role.name, "foo")
    with pytest.raises(InputError):
        cmd.main()


@pytest.mark.parametrize("extension", ["", CONFIG_EXT])
def test_symlink_created(fs, fake_files, extension):
    """A symlink is created for the role."""
    config_name = fake_files.role_config2.name + extension

    cmd = RoleCommand(fake_files.role.name, config_name)
    cmd.main()

    symlink_path = fake_files.role.path + CONFIG_EXT
    assert os.path.islink(symlink_path)
    assert os.readlink(symlink_path) == fake_files.role_config2.path
