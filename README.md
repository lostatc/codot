# codot
This repository is still under construction.

codot is a program for consolidating your dotfiles so that settings for
multiple applications can be modified from one set of files.

The Unix philosophy that every program should have a single responsibility
often means that users are left with their personal configurations and
customizations spread across multiple files that need to be tracked down and
modified separately. These config files often use different formats and
inconsistent setting names.

This program is meant to provide a simple text-based interface for
consolidating settings from multiple different programs into one or more files
for easy modification by the user. It allows you to edit your settings in one
place with one simple format and custom setting names. You decide how your
config files are organized and can group settings by function instead of by
program.

Cross-application customizations like color schemes and keybindings can be set
once instead of having to be set for each program separately. With *roles*, you
can easily swap out different color schemes or any other group of settings that
you define.

codot works with any program that uses plain-text files for configuration, no
matter the format. It is designed to work with most dotfile managers. See the
full documentation below for more details.

[Documentation](https://codot.readthedocs.io/en/latest/index.html)

## Installation
#### Dependencies
* python >= 3.5
* pyinotify
* Sphinx

#### Installing from source
Run the following commands in the downloaded source directory.
```
make
sudo make install
```

#### Post-install
Run the following command to generate all the necessary program files in the
current user's home directory.
```
codot init
```

The program comes with a daemon that monitors the filesystem and automatically
propogates changes to config files. To start it and set it to auto-start on
login, run the following commands.
```
systemctl --user start codot.service
systemctl --user enable codot.service
```
