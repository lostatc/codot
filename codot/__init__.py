"""Consolidate your dotfiles."""
import os
import sys

HOME_DIR = os.path.expanduser("~/")
XDG_CONFIG_HOME = os.getenv("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))

PROGRAM_DIR = os.path.join(XDG_CONFIG_HOME, "codot")
TEMPLATES_DIR = os.path.join(PROGRAM_DIR, "templates")
CONFIG_DIR = os.path.join(PROGRAM_DIR, "config")
PRIORITY_FILE = os.path.join(PROGRAM_DIR, "priority")
SETTINGS_FILE = os.path.join(PROGRAM_DIR, "settings.conf")
INFO_FILE = os.path.join(PROGRAM_DIR, "info.json")

CONFIG_EXT = ".conf"

if sys.stdout.isatty():
    ANSI_NORMAL = "\x1b[0m"
    ANSI_GREEN = "\x1b[32m"
    ANSI_RED = "\x1b[31m"
else:
    ANSI_NORMAL = ANSI_GREEN = ANSI_RED = ""
