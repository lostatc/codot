SYNOPSIS
========
codot [*global_options*] *command* [*command_options*] [*command_args*]

DESCRIPTION
===========
**codot** is a program for consolidating your dotfiles so that settings for
multiple applications can be modified from one set of files.

Concepts
--------
Source File
    A source file is a file created by an application to allow the user to
    configure that application (e.g. ~/.vimrc). There is an example source file
    under EXAMPLES_.

Template File
    A template file is a copy of a source file that has had certains values
    replaced with user-defined identifiers.

    All template files go in the 'templates' directory (see FILES_), which
    mimics the file structure under the user's home directory. That means that
    the template file for a config file located at ~/.config/foo will be
    located at .config/foo under the templates directory, and that every
    template file should correspond to exactly one source file. Template files
    are ignored unless the corresponding source file exists. There is an
    example template file under EXAMPLES_.

Config File
    A config file is a file created by the user to consolidate settings from
    multiple applications. Config files have the following format:

    * Lines starting with a hash symbol '#' serve as comments.
    * Options in this file consist of key-value pairs separated by an equals
      sign '=', where each key corresponds to the name of an identifier in one
      or more template files.

    Whenever the **sync** command is run, identifiers in each template file are
    replaced with their corresponding values from the config files, and those
    template files then overwrite the source files they were derived from.

    Config files go in the 'config' directory (see FILES_), and each config
    file must have the '.conf' extension. Config files are ignored unless their
    names are included in the 'priority' file (see FILES_), and their order in
    this file determines which config files take precedence when the same
    identifier appears in multiple config files. There is an example config
    file and an example 'priority' file under EXAMPLES_.

Identifier
    An identifier is a string used in one or more template files to represent a
    value in the corresponding source files. Each identifier has a name, which
    is an alphanumeric substring that corresponds to the name of an option in
    one or more config files. The default identifier format is '{{%s}}', where
    '%s' represents the name of the identifier, but this can be changed in the
    'settings.conf' file (see FILES_). The format of an identifier should be
    such that it doesn't conflict with the syntax used in any of the source
    files. Identifers in tempalte files can not span multiple lines.

Role
    A role is a way for multiple config files containing the same options to be
    swapped out easily. Example use cases could include color schemes or
    keybindings. A role consists of multiple config files in a subdirectory of
    the 'config' directory (see FILES_), only one of which can be selected at
    any one time. The name of this subdirectory determines the name of the
    role. There is a symlink in the 'config' directory which points to the
    selected role under the subdirectory, the name of which is the name of the
    role plus the '.conf' extension.  The selected config file for a role can
    be switched easily using the **role** command. The 'priority' file should
    contain the name of the role instead of the name of any individual config
    file.

Daemon
------
The daemon monitors the filesystem for changes and automatically runs the
**sync** command whenever a config file, a template file or the 'priority' file
is modofied.

GLOBAL OPTIONS
==============
**--help**
    Display a usage message and exit.

**--version**
    Print the version number and exit.

**--debug**
    Print a full stack trace instead of an error message if an error occurs.

**-q**, **--quiet**
    Suppress all non-error output.

COMMANDS
========
**sync** [*options*]
    Propogate changes in all config files and roles to all source files for
    which there is a template file, but only if those source files have not
    been modified since the last sync.

    **-o**, **--overwrite**
        Overwrite the source files even if they've been modified since the last
        sync.

**role** [*role_name* [*config_name*]]
    Make *config_name* the currently selected config file in the role named
    *role_name*. If *config_name* is not specified, print a list of config
    files available for that role and show which one is currently selected. If
    *role_name* is not specified, print a table of all roles and their selected
    config files.

EXAMPLES
========
This is an example of a source file. ::

    bar {
            status_command i3blocks
            position top
            font pango:DejaVuSans 12

            colors {
                statusline	#e0e0e0
                separator	#838383
                background	#212121
            }
    }

This is an example of a template file. ::

    bar {
            status_command i3blocks
            position top
            font pango:{{Typeface}} {{FontSize}}

            colors {
                statusline	{{ForegroundColor}}
                separator	{{AccentColor}}
                background	{{BackgroundColor}}
            }
    }

This is an example of a config file. ::

    # These are colors for the cross-application color scheme.
    ForegroundColor=#e0e0e0
    AccentColor=#838383
    BackgroundColor=#212121

    # These are cross-appliation font settings.
    Typeface=DejaVuSans
    FontSize=12

This is an example of what the file structure under the **codot** program
directory could look like. ::

    templates/
        .vimrc
        .config/
            i3/
                config
    config/
        desktop.conf
        color_scheme/
            solarized.conf
            dracula.conf
        color_scheme.conf -> color_scheme/solarized.conf
    priority
    settings.conf

This is an example of what the the 'priority' file could look like. ::

    desktop
    color_scheme

FILES
=====
~/.config/codot/
    This is the **codot** program directory. The program will respect
    XDG_CONFIG_HOME and, if it is set, put the directory there instead.

    templates/
        This directory is where all template files are stored. The file
        structure under this directory should mimic the file structure under
        the user's home directory.

    config/
        This directory is where all config files and roles are stored. Config
        files must have a '.conf' extension.

    priority
        This is a plain text file which stores the names of all enabled config
        files and roles, one per line. Config files not in this list are
        ignored. Entries higher up in the list take priority over entries lower
        down the list when the same identifiers appear in multiple config
        files.

    settings.conf
        This file is for configuring the behavior of **codot**.
