# codot
This repository is still under construction.

codot is a program for consolidating your dotfiles so that settings for
multiple applications can be modified from one set of files.

#### Consolidated
The Unix philosophy that every program should have a single responsibility can
be problematic when each program needs to be configured separately. Instead of
tracking down the individual config files for your window manager, terminal
emulator and status bar, codot allows you to edit all of your settings in one
place with the same text-based format you're familiar with. You can choose what
config options are called and separate them by function instead of by program.

#### Centralized
codot makes theming easy by allowing you to set up your color scheme and font
config once instead of on a per-program basis. When you want to make changes,
those changes propogate to each of your programs. With *roles*, you can
pre-define separate sets of config values and switch between them easily.

#### Interoperable
codot works with any program that uses plain text files for configuration, and
allows you to edit your consolidated config options using that same interface.
Because it's based on plain text, it works with all sorts of dotfile managers.

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
The program comes with a daemon that monitors the filesystem and automatically
propogates changes to config files. To start it and set it to auto-start on
login, run the following commands.
```
systemctl --user start codot.service
systemctl --user enable codot.service
```
