"""Consolidate your dotfiles."""

import os

PROGRAM_DIR = os.path.join(
    os.getenv("XDG_CONFIG_DIR", os.path.expanduser("~/.config")), "codot")
TEMPLATES_DIR = os.path.join(PROGRAM_DIR, "templates")
CONFIG_DIR = os.path.join(PROGRAM_DIR, "config")
PRIORITY_FILE = os.path.join(PROGRAM_DIR, "priority")
SETTINGS_FILE = os.path.join(PROGRAM_DIR, "settings.conf")
INFO_FILE = os.path.join(PROGRAM_DIR, "info.json")
