"""Program-wide exceptions.

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


class ProgramError(Exception):
    """Base exception for errors anticipated during normal operation."""


class UserInputError(ProgramError):
    """Raised whenever user-provided input is invalid."""


class StatusError(ProgramError):
    """Raised whenever there is an issue with the status of the program."""


class FileParseError(ProgramError):
    """Raised whenever there is an issue parsing a file."""
