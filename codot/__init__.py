"""Consolidate your dotfiles."""
import os

HOME_DIR = os.path.expanduser("~/")
XDG_CONFIG_HOME = os.getenv("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))

PROGRAM_DIR = os.path.join(XDG_CONFIG_HOME, "codot")
TEMPLATES_DIR = os.path.join(PROGRAM_DIR, "templates")
CONFIG_DIR = os.path.join(PROGRAM_DIR, "config")
PRIORITY_FILE = os.path.join(PROGRAM_DIR, "priority")
SETTINGS_FILE = os.path.join(PROGRAM_DIR, "settings.conf")
INFO_FILE = os.path.join(PROGRAM_DIR, "info.json")

CONFIG_EXT = ".conf"


class ProgramError(Exception):
    """Base exception for errors anticipated during normal operation."""


class InputError(ProgramError):
    """Raised whenever input is invalid."""


class StatusError(ProgramError):
    """Raised whenever there is an issue with the status of the program."""


class FileParseError(ProgramError):
    """Raised whenever there is an issue parsing a file."""
