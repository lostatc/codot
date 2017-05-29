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

from codot import FileParseError
from codot.utils import DictProperty


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
        """Parse individual config values."""
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

    Attributes:
        path: The path of the JSON file.
        raw_vals: A dictionary or list of values from the file.
    """
    def __init__(self, path) -> None:
        self.path = path
        self.raw_vals = None

    def read(self) -> None:
        """Read file into an object."""
        with open(self.path) as file:
            self.raw_vals = json.load(file)

    def write(self) -> None:
        """Write object to a file."""
        with open(self.path, "w") as file:
            json.dump(self.raw_vals, file, indent=4)


class ProgramConfigFile(ConfigFile):
    """Parse a program config file.

    Attributes:
        _true_vals: A list of strings that are recognized as boolean true.
        _false_vals: A list of strings that are recognized as boolean false.
        _req_keys: A list of config keys that must be included in the config
            file.
        _opt_keys: A list of config keys that may be commented out or omitted.
        _all_keys: A list of all keys that are recognized in the config file.
        _bool_keys: A subset of config keys that must have boolean values.
        _defaults: A dictionary of default string values for optional config
            keys.
        path: The path of the configuration file.
        raw_vals: A dict of unmodified config value strings.
        vals: A dict property of parsed config values.
    """
    _true_vals = ["yes", "true"]
    _false_vals = ["no", "false"]
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
        """Parse individual config values.

        Returns:
            IdentifierFormat: Input value unmodified as a str.
            OverwriteAlways: Input value converted to a bool.
        """
        if key in self.raw_vals:
            value = self.raw_vals[key]
        elif key in self._defaults:
            value = self._defaults[key]
        else:
            value = None

        if key in self._bool_keys:
            if isinstance(value, str):
                if value.lower() in self._true_vals:
                    value = True
                elif value.lower() in self._false_vals:
                    value = False

        return value

    @vals.setter
    def vals(self, key: str, value: str) -> None:
        """Set individual config values."""
        self.raw_vals[key] = value

    def _check_value(self, key: str, value: str) -> Optional[str]:
        # Check boolean values.
        if (key in self._bool_keys
                and value.lower() not in (self._true_vals + self._false_vals)):
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

    Attributes:
        raw_vals: A dictionary of raw string values from the file.
        vals: A dict property of parsed values from the file.
    """
    def __init__(self, path) -> None:
        super().__init__(path)
        self.raw_vals = {}

    @DictProperty
    def vals(self, key) -> Any:
        """Parse individual values from the info file.

        Returns:
            LastSync: Input value converted to the number of seconds since the
                epoch.
        """
        if key in self.raw_vals:
            value = self.raw_vals[key]
        else:
            value = None

        if value is not None:
            if key == "LastSync":
                value = datetime.datetime.strptime(
                    value, "%Y-%m-%dT%H:%M:%S.%f").replace(
                        tzinfo=datetime.timezone.utc).timestamp()

        return value

    @vals.setter
    def vals(self, key, value) -> None:
        """Set individual values."""
        if value is not None:
            if key == "LastSync":
                # Use strftime() instead of isoformat() because the latter
                # doesn't print the decimal point if the microsecond is 0,
                # which would prevent it from being parsed by strptime().
                value = datetime.datetime.utcfromtimestamp(
                    value).strftime("%Y-%m-%dT%H:%M:%S.%f")
        self.raw_vals[key] = value

    def generate(self) -> None:
        """Generate info for a new profile.

        JSON Values:
            LastSync: The date and time (UTC) of the last sync on the profile.

        Args:
            name: The name of the profile to use for the unique ID.
        """
        self.raw_vals.update({
            "LastSync": None,
            })
        self.vals["LastSync"] = time.time()
        self.write()
