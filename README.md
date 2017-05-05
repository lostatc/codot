# codot
This repository is still under construction.

codot is a program for consolidating your dotfiles so that settings for
multiple applications can be modified from one set of files.

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
