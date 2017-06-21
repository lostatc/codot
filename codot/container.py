"""Classes for managing stored data.

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
import re
import json
import datetime
import time
from typing import Any, Optional

from codot import SETTINGS_FILE, INFO_FILE
from codot.exceptions import FileParseError
from codot.utils import DictProperty


class ProgramData:
    """Access persistently stored data."""
    def __init__(self) -> None:
        self._cfg_file = ProgramConfigFile(SETTINGS_FILE)
        self._info_file = ProgramInfoFile(INFO_FILE)

    def read(self) -> None:
        self._cfg_file.read()
        self._cfg_file.check_all()
        self._info_file.read()

    def generate(self) -> None:
        """Generate files storing persistent data."""
        self.last_sync = time.time()
        self.write()

    def write(self) -> None:
        self._info_file.write()

    @property
    def overwrite_always(self) -> bool:
        """Always overwrite source files."""
        raw_value = self._cfg_file.vals["OverwriteAlways"]
        if raw_value in self._cfg_file.true_vals:
            return True
        elif raw_value in self._cfg_file.false_vals:
            return False

    @overwrite_always.setter
    def overwrite_always(self, value) -> None:
        self._cfg_file.vals["OverwriteAlways"] = value

    @property
    def id_format(self) -> str:
        """The format for identifiers in the template files."""
        return self._cfg_file.vals["IdentifierFormat"]

    @id_format.setter
    def id_format(self, value) -> None:
        self._cfg_file.vals["IdentifierFormat"] = value

    @property
    def last_sync(self) -> float:
        """The time of the last sync in seconds since the epoch."""
        raw_value = self._info_file.vals["LastSync"]
        return datetime.datetime.strptime(
            raw_value, "%Y-%m-%dT%H:%M:%S.%f").replace(
            tzinfo=datetime.timezone.utc).timestamp()

    @last_sync.setter
    def last_sync(self, value: float) -> None:
        # Use strftime() instead of isoformat() because the latter
        # doesn't print the decimal point if the microsecond is 0,
        # which would prevent it from being parsed by strptime().
        self._info_file.vals["LastSync"] = datetime.datetime.utcfromtimestamp(
            value).strftime("%Y-%m-%dT%H:%M:%S.%f")


class ConfigFile:
    """Parse a configuration file.

    Attributes:
        COMMENT_REGEX: A regex object that denotes a comment line.
        SEPARATOR: The first instance of this character on each line of the
            config file separates the key from the value.
        path: The path of the configuration file.
        raw_vals: A dict of unmodified config value strings.
        vals: This dict property is exactly the same as raw_vals. It exists so
            that subclasses can use the same interface.
    """
    COMMENT_REGEX = re.compile(r"^\s*#")
    SEPARATOR = "="

    def __init__(self, path: str) -> None:
        self.path = path
        self.raw_vals = {}

    @DictProperty
    def vals(self, key) -> str:
        """Return individual config values."""
        return self.raw_vals[key]

    @vals.setter
    def vals(self, key: str, value: str) -> None:
        """Set individual config values."""
        self.raw_vals[key] = value

    def read(self) -> None:
        """Parse file for key-value pairs and save in a dictionary."""
        try:
            with open(self.path) as file:
                for line in file:
                    # Skip line if it is a comment.
                    if (not self.COMMENT_REGEX.search(line)
                            and self.SEPARATOR in line):
                        key, value = line.partition(self.SEPARATOR)[::2]
                        self.raw_vals[key.strip()] = value.strip()
        except OSError:
            raise FileParseError("could not open the configuration file")


class JSONFile:
    """Parse a JSON-formatted file.

    Args:
        path: The path of the JSON file.

    Attributes:
        path: The path of the JSON file.
        vals: A dictionary or list of values from the file.
    """
    def __init__(self, path) -> None:
        self.path = path
        self.vals = None

    def read(self) -> None:
        """Read all files storing persistent data."""
        with open(self.path) as file:
            self.vals = json.load(file)

    def write(self) -> None:
        """Write object to a file."""
        with open(self.path, "w") as file:
            json.dump(self.vals, file, indent=4)


class ProgramConfigFile(ConfigFile):
    """Parse a program config file.

    Attributes:
        true_vals: A list of strings that are recognized as boolean true.
        false_vals: A list of strings that are recognized as boolean false.
        _req_keys: A list of config keys that must be included in the config
            file.
        _opt_keys: A list of config keys that may be commented out or omitted.
        _all_keys: A list of all keys that are recognized in the config file.
        _bool_keys: A subset of config keys that must have boolean values.
        _defaults: A dictionary of default string values for optional config
            keys.
        path: The path of the configuration file.
        raw_vals: A dict of unmodified config value strings.
        vals: A dict property that returns values from raw_vals but defaults to
            value from _defaults.
    """
    true_vals = ["yes", "true"]
    false_vals = ["no", "false"]
    _req_keys = []
    _opt_keys = [
        "IdentifierFormat", "OverwriteAlways"
        ]
    _all_keys = _req_keys + _opt_keys
    _bool_keys = [
        "OverwriteAlways"
        ]
    _defaults = {
        "IdentifierFormat": "{{%s}}",
        "OverwriteAlways": "no"
        }

    @DictProperty
    def vals(self, key) -> Any:
        """Get defaults of corresponding raw values are unset."""
        if key in self.raw_vals:
            return self.raw_vals[key]
        elif key in self._defaults:
            return self._defaults[key]

    @vals.setter
    def vals(self, key: str, value: str) -> None:
        """Set individual config values."""
        self.raw_vals[key] = value

    def _check_value(self, key: str, value: str) -> Optional[str]:
        # Check boolean values.
        if (key in self._bool_keys
                and value.lower() not in (self.true_vals + self.false_vals)):
            return "must have a boolean value"

        if key == "IdentifierFormat":
            if not value:
                return "must not be blank"
            elif value.count("%s") < 1:
                return "must contain the variable '%s'"
            elif value.count("%s") > 1:
                return "must not contain more than one instance of '%s'"

    def check_all(self, check_empty=True, context="config file") -> None:
        """Check that file is valid and syntactically correct.

        Args:
            check_empty: Check empty/unset values.
            context: The context to show in the error messages.

        Raises:
            FileParseError: There were missing, unrecognized or invalid options
                in the config file.
        """
        parse_errors = []

        # Check that all key names are valid.
        missing_keys = set(self._req_keys) - self.raw_vals.keys()
        unrecognized_keys = self.raw_vals.keys() - set(self._all_keys)
        for key in missing_keys:
            parse_errors.append(
                "{0}: missing required option '{1}'".format(context, key))
        for key in unrecognized_keys:
            parse_errors.append(
                "{0}: unrecognized option '{1}'".format(context, key))

        # Check values for valid syntax.
        for key, value in self.raw_vals.items():
            if check_empty or not check_empty and value:
                err_msg = self._check_value(key, value)
                if err_msg:
                    parse_errors.append(
                        "{0}: '{1}' {2}".format(context, key, err_msg))

        if parse_errors:
            raise FileParseError(*parse_errors)


class ProgramInfoFile(JSONFile):
    """Parse a json-formatted file for string program metadata.

    Args:
        path: The path of the JSON file.

    Attributes:
        vals: A dict of values from the file.
    """
    def __init__(self, path: str) -> None:
        super().__init__(path)
        self.vals = {}
