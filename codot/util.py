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
from typing import Collection


def rshave(string: str, substring: str) -> str:
    """Remove the first occurrence of a substring starting from the right.

    Args:
        string: The string to remove the substring from.
        substring: The substring to remove from the string. If this is an empty
            string or None, then nothing is removed.

    Returns:
        The original string with the substring removed.
    """
    if substring:
        return "".join(string.rsplit(substring, 1))
    else:
        return string


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


def print_table(headers: list, data: Collection[tuple]) -> None:
    """Print input values in a formatted ascii table.

    All values in the table are left-aligned, and columns are as wide as
    their longest value.

    Args:
        data: The values used to fill the body of the table. Each item in this
            collection represents a row in the table.
        headers: The values to use as column headings.
    """
    column_lengths = []
    for content, header in zip(zip(*data), headers):
        column = [str(item) for item in [*content, header]]
        column_lengths.append(len(max(column, key=len)))

    # Print the table header.
    print(" | ".join([
        "{0:<{1}}".format(name, width)
        for name, width in zip(headers, column_lengths)]))

    # Print the separator between the header and body.
    print("-+-".join(["-"*length for length in column_lengths]))

    # Print the table body.
    for row in data:
        print(" | ".join([
            "{0:<{1}}".format(field, width)
            for field, width in zip(row, column_lengths)]))


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
