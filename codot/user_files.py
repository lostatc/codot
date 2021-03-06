"""Read and write files.

Copyright © 2017-2018 Garrett Powell <garrett@gpowell.net>

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
import os
from typing import List, Tuple, Dict, Optional

from codot import CONFIG_EXT, HOME_DIR
from codot.container import ConfigFile
from codot.utils import rm_ext, add_ext, rec_scan


class TemplateFile:
    """Manage a template file.

    Args:
        path: The path of the template file relative to the base directory.
        base_dir: The path of the base directory containing all template files.

    Attributes:
        path: The absolute path of the template file.
        base_dir: The path of the base directory containing all template files.
    """
    def __init__(self, path: str, base_dir: str) -> None:
        self.path = os.path.join(base_dir, path)
        self.base_dir = base_dir

    @property
    def source_path(self) -> Optional[str]:
        """The path of the template file's corresponding source file.

        Returns:
            The path of the source file.
        """
        return os.path.join(
            HOME_DIR, os.path.relpath(self.path, self.base_dir))

    def get_identifier_names(self, id_format: str) -> List[str]:
        """Get all identifier names used in the template file.

        Args:
            id_format: The format of identifiers in the template file, with
                "%s" representing the name of the identifier.

        Returns:
            A deduplicated list of names of identifiers.
        """
        identifier_names = set()
        identifier_regex = re.compile(
            re.escape(id_format).replace(r"\%s", r"([\w-]+)"))

        with open(self.path) as file:
            for line in file:
                for match_string in identifier_regex.findall(line):
                    identifier_names.add(match_string)

        return list(identifier_names)


class UserConfigFile(ConfigFile):
    """Manage a user-created config file."""
    @property
    def name(self) -> str:
        """Get the basename of the file without the ".conf" extension."""
        return rm_ext(os.path.basename(self.path), CONFIG_EXT)


class Role:
    """Manage a role.

    Attributes:
        name: The name of the role.
        base_dir: The base directory containing all roles.
    """
    def __init__(self, name: str, base_dir: str) -> None:
        self.name = name
        self.base_dir = base_dir

    def get_configs(self) -> List[UserConfigFile]:
        """Get a sorted list of available configs for the role.

        Returns:
            A sorted list containing a UserConfigFile object for each config
            file in the role.
        """
        config_paths = []
        for entry in os.scandir(self.dir_path):
            if entry.is_file() and entry.name.endswith(CONFIG_EXT):
                config_paths.append(entry.path)
        config_paths.sort()
        return [UserConfigFile(config_path) for config_path in config_paths]

    def get_config_by_name(self, config_name: str) -> Optional[UserConfigFile]:
        """Get a config belonging to the role by its name.

        This accepts the name of a config with or without the extension.

        Returns:
            A UserConfigFile object for the config if it exists or None if it
            does not.
        """
        for config in self.get_configs():
            if config.name == rm_ext(config_name, CONFIG_EXT):
                return config
        return None

    @property
    def dir_path(self) -> str:
        """The path of the directory containing the role's config files.

        Returns:
            The path as a string.
        """
        return os.path.join(self.base_dir, self.name)

    @property
    def symlink_path(self) -> str:
        """The path of the symlink that points to the selected config file.

        Returns:
            The path as a string.
        """
        return os.path.join(self.base_dir, add_ext(self.name, CONFIG_EXT))

    @property
    def selected(self) -> UserConfigFile:
        """The selected config file for the role.

        Returns:
            A UserConfigFile object for the selected config file or None if
            there is none.
        """
        link_destination = os.readlink(self.symlink_path)
        if not os.path.isabs(link_destination):
            link_destination = os.path.join(
                os.path.dirname(self.symlink_path), link_destination)
        return UserConfigFile(link_destination)


class UserFiles:
    """Read and write user-created files.

    Attributes:
        config_dir: The path of the directory containing the user's config
            files.
        templates_dir: The path of the directory containing the user's
            template files.
    """
    def __init__(self, config_dir: str, templates_dir: str) -> None:
        self.config_dir = config_dir
        self.templates_dir = templates_dir

    def get_configs(self, enter_roles=False) -> List[UserConfigFile]:
        """Get a list of all configs.

        Args:
            enter_roles: Include the non-selected configs from each role.

        Returns:
            A sorted list containing a UserConfigFile object for each config
            file and role in the config directory.
        """
        if enter_roles:
            scan_func = rec_scan
        else:
            scan_func = os.scandir

        config_paths = []
        for entry in scan_func(self.config_dir):
            if entry.name.endswith(CONFIG_EXT):
                config_paths.append(entry.path)
        config_paths.sort()

        return [UserConfigFile(path) for path in config_paths]

    def get_config_values(self) -> Dict[str, str]:
        """Get key-value pairs from all enabled configs and roles.

        Returns:
            A dict of key-value pairs.
        """
        config_values = {}
        # Reverse the order so that values from configs that sort earlier in
        # the list override those from configs that sort later in the list.
        for config_file in reversed(self.get_configs(enter_roles=False)):
            config_file.read()
            config_values.update(config_file.raw_vals)

        return config_values

    def get_templates(self) -> List[TemplateFile]:
        """Get a list of all templates.

        Template files without a corresponding source file are skipped.

        Returns:
            A list containing a TemplateFile object for each template in the
            templates directory.
        """
        templates = []
        for entry in rec_scan(self.templates_dir):
            if not entry.is_file():
                continue

            template = TemplateFile(
                os.path.relpath(entry.path, self.templates_dir),
                self.templates_dir)

            try:
                if not os.path.isfile(template.source_path):
                    continue
            except FileNotFoundError:
                continue

            templates.append(template)

        return templates

    def get_roles(self) -> List[Role]:
        """Get a list of all roles.

        Returns:
            A list containing a Role object for each role in the config
            directory.
        """
        role_names = []
        for entry in os.scandir(self.config_dir):
            if entry.is_dir():
                role_names.append(entry.name)

        return [Role(role_name, self.config_dir) for role_name in role_names]
