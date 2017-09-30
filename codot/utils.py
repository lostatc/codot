"""Miscellaneous utilities.

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
import subprocess
from typing import List

from codot import HOME_DIR


def rm_ext(orig_string: str, substring: str) -> str:
    """Remove the first occurrence of a substring starting from the right.

    Args:
        orig_string: The string to remove the substring from.
        substring: The substring to remove from the string. If this is an empty
            string or None, then nothing is removed.

    Returns:
        The original string with the substring removed.
    """
    if substring and orig_string.endswith(substring):
        return orig_string[:-len(substring)]
    else:
        return orig_string


def add_ext(orig_string: str, substring: str) -> str:
    """Append a substring to the end if it's not already there.

    Args:
        orig_string: The string to add the substring to.
        substring: The substring to add to the string. If this already exists,
            nothing is added.

    Returns:
        The original string with the substring added.
    """
    if substring:
        return rm_ext(orig_string, substring) + substring
    else:
        return orig_string


def contract_user(path: str) -> str:
    """Do the opposite of os.path.expanduser.

    Args:
        path: The absolute file path to modify.

    Returns:
        A new file path with the user's home directory replaced with a tilda.
    """
    return os.path.join("~", os.path.relpath(path, HOME_DIR))


def rec_scan(path: str):
    """Recursively scan a directory tree and yield an os.DirEntry object.

    Args:
        path: The path of the directory to scan.

    Yields:
        os.DirEntry objects for each path under the directory recursively.
    """
    for entry in os.scandir(path):
        yield entry
        if entry.is_dir(follow_symlinks=False):
            yield from rec_scan(entry.path)


def open_text_editor(filepath: str) -> int:
    """Open the default text editor on a given file path.

    Args:
        filepath: The path of the file to edit.

    Returns:
        The return code of the command.
    """
    editors = [
        os.getenv("VISUAL"), os.getenv("EDITOR"), "nano", "vi"]
    edit_command = [
        editor for editor in editors if editor is not None][0]
    full_command = [edit_command, filepath]

    return subprocess.run(full_command).returncode


class DictProperty:
    """A property for the getting and setting of individual dictionary keys."""
    class _Proxy:
        def __init__(self, obj, fget, fset, fdel):
            self._obj = obj
            self._fget = fget
            self._fset = fset
            self._fdel = fdel

        def __getitem__(self, key):
            if self._fget is None:
                raise TypeError("can't read item")
            return self._fget(self._obj, key)

        def __setitem__(self, key, value):
            if self._fset is None:
                raise TypeError("can't set item")
            self._fset(self._obj, key, value)

        def __delitem__(self, key):
            if self._fdel is None:
                raise TypeError("can't delete item")
            self._fdel(self._obj, key)

    def __init__(self, fget=None, fset=None, fdel=None, doc=None):
        self._fget = fget
        self._fset = fset
        self._fdel = fdel
        self.__doc__ = doc

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return self._Proxy(obj, self._fget, self._fset, self._fdel)

    def getter(self, fget):
        return type(self)(fget, self._fset, self._fdel, self.__doc__)

    def setter(self, fset):
        return type(self)(self._fget, fset, self._fdel, self.__doc__)

    def deleter(self, fdel):
        return type(self)(self._fget, self._fset, fdel, self.__doc__)
