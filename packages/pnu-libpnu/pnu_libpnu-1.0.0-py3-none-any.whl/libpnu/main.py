#!/usr/bin/env python
""" libpnu - Common utility functions for the PNU project
License: 3-clause BSD (see https://opensource.org/licenses/BSD-3-Clause)
Author: Hubert Tournier
"""

import getpass
import logging
import os
import pwd
import signal
import sys

# Version string used by the what(1) and ident(1) commands:
ID = "@(#) $Id: libpnu - Common utility functions for the PNU project v1.0.0 (February 28, 2022) by Hubert Tournier $"


################################################################################
def initialize_debugging(program_name):
    """Set up debugging"""
    console_log_format = program_name + ": %(levelname)s: %(message)s"
    logging.basicConfig(format=console_log_format, level=logging.DEBUG)
    logging.disable(logging.INFO)


################################################################################
def handle_interrupt_signals(handler_function):
    """Process interrupt signals"""
    signal.signal(signal.SIGINT, handler_function)
    signal.signal(signal.SIGPIPE, handler_function)


################################################################################
def locate_directory(directory):
    """Return a list of paths containing the specified directory"""
    directories_list = []

    parts = []
    if os.sep in directory:
        parts = directory.split(os.sep)
    elif os.altsep and os.altsep in directory:
        parts = directory.split(os.altsep)
    else:
        parts = [directory]

    # Make absolute paths relative:
    if parts and not parts[0]:
        parts = parts[1:]

    # For example, if the argument is "/usr/local/etc/man.d", we'll search:
    # "usr/local/etc/man.d", "local/etc/man.d", "etc/man.d" and "man.d"
    # in a list of user's local Python package directories
    # and system wide Python package directories
    while parts:
        directory = os.sep.join(parts)

        # First searching in the user's local Python packages directory:
        if os.name == "posix":
            if "HOME" in os.environ:
                dir_tested = os.environ["HOME"] + os.sep + ".local" + os.sep + directory
                if os.path.isdir(dir_tested):
                    directories_list.append(dir_tested)
            else:
                user = getpass.getuser()
                if user:
                    home_directory = pwd.getpwnam(user)[5]
                    dir_tested = home_directory + os.sep + ".local" + os.sep + directory
                    if os.path.isdir(dir_tested):
                        directories_list.append(dir_tested)

        elif os.name == "nt":
            last_part = os.sep + "python" + os.sep + directory
            mid_part = os.sep + "appdata" + os.sep + "roaming"
            if "APPDATA" in os.environ:
                dir_tested = os.environ["APPDATA"] + last_part
            elif "HOMEPATH" in os.environ:
                dir_tested = os.environ["HOMEPATH"] + mid_part + last_part
            elif "USERPROFILE" in os.environ:
                dir_tested = os.environ["USERPROFILE"] + mid_part + last_part
            if os.path.isdir(dir_tested):
                directories_list.append(dir_tested)

        # Next trying in Python's base installation prefix:
        dir_tested = sys.base_prefix + os.sep + directory
        if os.path.isdir(dir_tested):
            directories_list.append(dir_tested)

        # Remove the first part:
        parts = parts[1:]

    return directories_list


if __name__ == "__main__":
    sys.exit(0)
