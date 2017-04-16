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
