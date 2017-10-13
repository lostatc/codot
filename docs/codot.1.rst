=======
codot.1
=======
SYNOPSIS
========
codot [*global_options*] *command* [*command_options*] [*command_args*]

DESCRIPTION
===========
**codot** is a program for consolidating your dotfiles so that settings for
multiple applications can be modified from one set of files.

Terminology
-----------
Source File
    A source file is a file created by an application to allow the user to
    configure that application (e.g. ~/.vimrc). There is an example source file
    under EXAMPLES_.

Template File
    A template file is a copy of a source file that has had certain values
    replaced with user-defined identifiers. There is an example template file
    under EXAMPLES_.

Config File
    A config file is a file created by the user that acts as a centralized
    place to modify values from multiple source files. Config files have the
    following format:

    * Lines starting with a hash symbol '#' serve as comments.
    * Options are key-value pairs separated by an equals sign '=', where each
      key corresponds to the name of an identifier in one or more template
      files.

    Config files go in the 'config' directory (see FILES_) and each config file
    must have a '.conf' extension. There is an example config file under
    EXAMPLES_.

Identifier
    An identifier is a string used in a template file to signal where a value
    from a config file should be substituted in. Each identifier has a name,
    which corresponds to the name of an option in a config file. The default
    identifier format is '{{%s}},' where '%s' represents the name of the
    identifier. The same identifier name can be used more than once and in more
    than one template file.

Role
    A role a way to easily swap out different sets of config values. Each set
    of values goes in a separate config file, one of which can fill the role at
    a time. To create a role, put one or more config files in a subdirectory of
    the 'config' directory (see FILES_). The name of this subdirectory is the
    name of the role. The selected config file for a role can be switched using
    the **role** command.

Here are the steps for getting started with **codot**:

#. Identify which values from which source files you want to consolidate.
#. Use the **add-template** command to open the source files in your text
   editor. Then, replace the values you selected with identifiers. Name these
   identifiers whatever you want.
#. Create one or more config files that contain options named after the
   identifiers you created.
#. Populate those config files with values.
#. Start the daemon or run the **sync** command.

GLOBAL OPTIONS
==============
.. This imports documentation from the code.
.. linotype::
    :filepath: ../codot/cli.py
    :function: help_item
    :item_id: global_opts
    :children:

COMMANDS
========
.. This imports documentation from the code.
.. linotype::
    :filepath: ../codot/cli.py
    :function: help_item
    :item_id: commands
    :children:

    sync
        If the daemon is running, this command is run automatically whenever a
        config file or template file is modified.

EXAMPLES
========
This is an example of a source file.

.. code-block:: none
    :linenos:

    bar {
        status_command i3status
        position top
        font pango:DejaVuSans 12

        colors {
            statusline  #e0e0e0
            separator   #838383
            background  #212121
        }
    }

This is an example of a template file using the default identifier format.

.. code-block:: none
    :linenos:

    bar {
        status_command i3status
        position top
        font pango:{{Font}} {{FontSize}}

        colors {
            statusline  {{ForegroundColor}}
            separator   {{AccentColor}}
            background  {{BackgroundColor}}
        }
    }

This is an example of a config file.

.. code-block:: cfg
    :linenos:

    # These are colors for the cross-application color scheme.
    ForegroundColor=#e0e0e0
    AccentColor=#838383
    BackgroundColor=#212121

    # These are cross-appliation font settings.
    Font=DejaVuSans
    FontSize=12

FILES
=====
~/.config/codot/
    This is the **codot** program directory. The program will respect
    XDG_CONFIG_HOME and, if it is set, put the directory there instead.

    config/
        This directory is where all config files and roles are stored. Config
        files must have a '.conf' extension.

    templates/
        This directory is where all template files are stored. The file
        structure under this directory mimics the file structure under the
        user's home directory.

    settings.conf
        This file is for configuring the behavior of **codot**.
