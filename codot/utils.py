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
import re
import subprocess
from typing import List, Tuple

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


class BoxTable:
    """Format a table using box-drawing characters.

    This table allows for ANSI escape codes in the data. Each row must have
    the same number of columns. The contents of each row are left-aligned.
    Empty rows are converted to horizontal separators.

    Attributes:
        data: The table data, where each item is a row in the table. The first
            row makes up the table headers.
    """
    HORIZONTAL_CHAR = "\u2500"
    HEAVY_HORIZONTAL_CHAR = "\u2501"
    VERTICAL_CHAR = "\u2502"
    TOP_RIGHT_CHAR = "\u2510"
    TOP_LEFT_CHAR = "\u250c"
    BOTTOM_RIGHT_CHAR = "\u2518"
    BOTTOM_LEFT_CHAR = "\u2514"
    CROSS_CHAR = "\u253c"
    HEAVY_CROSS_CHAR = "\u253f"
    TOP_TEE_CHAR = "\u252c"
    BOTTOM_TEE_CHAR = "\u2534"
    LEFT_TEE_CHAR = "\u251c"
    HEAVY_LEFT_TEE_CHAR = "\u251d"
    RIGHT_TEE_CHAR = "\u2524"
    HEAVY_RIGHT_TEE_CHAR = "\u2525"
    ANSI_REGEX = re.compile("(\x1b\\[[0-9;]+m)")

    def __init__(self, data: List[Tuple[str, ...]]):
        if not all(len(row) == len(data[0]) for row in data):
            raise ValueError("each row must be the same length")
        self.data = data
        self._lengths = self._get_column_lengths()

    def _get_column_lengths(self) -> List[int]:
        """Get the length of each column in the table."""
        columns = [column for column in zip(*self.data)]
        lengths = []
        for column in columns:
            visible_column = [self.ANSI_REGEX.sub("", item) for item in column]
            lengths.append(len(max(visible_column, key=len)))
        return lengths

    def _get_separator(self, char: str) -> List[str]:
        """Get the inside portion of a separator row."""
        return [char * (length+2) for length in self._lengths]

    def _format_top_separator(self) -> str:
        """Format the top border of the table."""
        return (
            self.TOP_LEFT_CHAR
            + self.TOP_TEE_CHAR.join(self._get_separator(self.HORIZONTAL_CHAR))
            + self.TOP_RIGHT_CHAR)

    def _format_bottom_separator(self) -> str:
        """Format the top border of the table."""
        return (
            self.BOTTOM_LEFT_CHAR
            + self.BOTTOM_TEE_CHAR.join(
                self._get_separator(self.HORIZONTAL_CHAR))
            + self.BOTTOM_RIGHT_CHAR)

    def _format_header_separator(self) -> str:
        """Format the row separator."""
        return (
            self.HEAVY_LEFT_TEE_CHAR
            + self.HEAVY_CROSS_CHAR.join(
                self._get_separator(self.HEAVY_HORIZONTAL_CHAR))
            + self.HEAVY_RIGHT_TEE_CHAR)

    def _format_inside_separator(self) -> str:
        """Format the row separator."""
        return (
            self.LEFT_TEE_CHAR
            + self.CROSS_CHAR.join(self._get_separator(self.HORIZONTAL_CHAR))
            + self.RIGHT_TEE_CHAR)

    def _format_row(self) -> str:
        """Format a row containing data."""
        for row in self.data:
            if not any(row):
                yield self._format_inside_separator()
            else:
                # str.format() can't be used for padding because it doesn't
                # ignore ANSI escape sequences.
                padding = [
                    length - len(self.ANSI_REGEX.sub("", text))
                    for text, length in zip(row, self._lengths)]
                inside = " {} ".format(self.VERTICAL_CHAR).join(
                    text + " "*spaces for text, spaces in zip(row, padding))

                yield (
                    self.VERTICAL_CHAR
                    + " " + inside + " "
                    + self.VERTICAL_CHAR)

    def format(self) -> str:
        """Format the table data into a string.

        Returns:
            The table as a string.
        """
        data_rows = self._format_row()
        table_lines = [
            self._format_top_separator(),
            next(data_rows),
            self._format_header_separator(),
            *data_rows,
            self._format_bottom_separator()]

        return "\n".join(table_lines)
