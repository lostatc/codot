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
from typing import Any, Optional

from codot.exceptions import FileParseError
from codot.misc import DictProperty


class ConfigFile:
    """Parse a configuration file.

    Attributes:
        _comment_regex: Regex that denotes a comment line.
        path: The path of the configuration file.
        raw_vals: A dict of unmodified config value strings.
        vals: This dict is exactly the same as raw_vals. It exists so that
            subclasses can use the same interface.
    """
    _comment_regex = re.compile(r"^\s*#")

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
                    if (not self._comment_regex.search(line)
                            and re.search("=", line)):
                        key, value = line.partition("=")[::2]
                        self.raw_vals[key.strip()] = value.strip()
        except OSError:
            raise FileParseError("could not open the configuration file")

    def write(self, template_path: str) -> None:
        """Generate a new config file based on the input file."""
        try:
            with open(template_path) as infile, open(
                    self.path, "w") as outfile:
                for line in infile:
                    # Skip line if it is a comment.
                    if (not self._comment_regex.search(line)
                            and re.search("=", line)):
                        key, value = line.partition("=")[::2]
                        key = key.strip()
                        if key not in self.raw_vals:
                            continue
                        # Substitute value in the input file with the value in
                        # self.raw_vals.
                        line = key + "=" + self.raw_vals.get(key, "") + "\n"
                    outfile.write(line)

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
        _all_keys: A list of all keys that are recognized in the config file.
        _bool_keys: A list of keys that must have boolean values.
        _default_vals: A dict of default values for config keys.
        path: The path of the configuration file.
        raw_vals: A dict of unmodified config value strings.
        vals: A dict property of parsed config values.
    """
    _true_vals = ["yes", "true"]
    _false_vals = ["no", "false"]
    _all_keys = [
        "IdentifierFormat", "OverwriteAlways"
        ]
    _bool_keys = [
        "OverwriteAlways"
        ]
    _default_vals = {
        "IdentifierFormat": "{{%s}}",
        "OverwriteAlways":  "no"
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
        elif key in self._default_vals:
            value = self._default_vals[key]
        else:
            value = None

        if key in self._bool_keys:
            if isinstance(value, str):
                if value.lower() in self._true_vals:
                    value = True
                elif value.lower() in self._false_vals:
                    value = False

        return value

    def _check_value(self, key: str, value: str) -> Optional[str]:
        # Check boolean values.
        if key in self._bool_keys and value:
            if value.lower() not in (self._true_vals + self._false_vals):
                return "must have a boolean value"

        if key == "IdentifierFormat":
            if not value:
                return "must not be blank"
            elif not re.search("%s", value):
                return "must contain the variable '%s'"

    def check_all(self, check_empty=True, context="config file") -> None:
        errors = []

        # Check that all key names are valid.
        unrecognized_keys = self.raw_vals.keys() - set(self._all_keys)
        for key in unrecognized_keys:
            errors.append(
                "{0}: unrecognized option '{1}'".format(context, key))

        # Check values for valid syntax.
        for key, value in self.raw_vals.items():
            if check_empty or not check_empty and value:
                err_msg = self._check_value(key, value)
                if err_msg:
                    errors.append(
                        "{0}: '{1}' {2}".format(context, key, err_msg))

        if errors:
            raise FileParseError(*errors)


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
                    value, "%Y-%m-%dT%H:%M:%S").replace(
                        tzinfo=datetime.timezone.utc).timestamp()

        return value

    @vals.setter
    def vals(self, key, value) -> None:
        """Set individual values."""
        if value is not None:
            if key == "LastSync":
                value = datetime.datetime.utcfromtimestamp(
                    int(value)).strftime("%Y-%m-%dT%H:%M:%S")
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
        self.write()
