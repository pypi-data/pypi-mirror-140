#!/usr/bin/env python
""" libmanconf - library for handling man(1) and manpath(1) configuration files
License: 3-clause BSD (see https://opensource.org/licenses/BSD-3-Clause)
Author: Hubert Tournier
"""

import os
import sys

import libpnu

# Version string used by the what(1) and ident(1) commands:
ID = "@(#) $Id: libmanconf - library for handling man(1) and manpath(1) configuration files v1.0.0 (February 28, 2022) by Hubert Tournier $"


################################################################################
def _read_configuration_file(filename, debug_level):
    """Read a man(1) and manpath(1) configuration file"""
    config = ""
    paths = ""
    locales = ""
    processors = []

    if os.path.isfile(filename):
        with open(filename, "r", encoding="utf-8") as file:
            if debug_level > 0:
                print("-- Parsing config file: %s" % filename, file=sys.stderr)

            for line in file:
                line = line.strip()

                if debug_level > 1:
                    print("--  %s" % line, file=sys.stderr)

                if line:
                    parts = line.split()

                    if parts[0] == "MANCONFIG":
                        if debug_level > 2:
                            print("--   MANCONFIG", file=sys.stderr)
                        if len(parts) == 2:
                            config = parts[1]

                    elif parts[0] == "MANPATH":
                        if debug_level > 2:
                            print("--   MANPATH", file=sys.stderr)
                        if len(parts) == 2:
                            if os.path.isdir(parts[1]):
                                if debug_level > 1:
                                    print("--  Adding %s to manpath" % parts[1], file=sys.stderr)
                                if paths:
                                    paths += ":" + parts[1]
                                else:
                                    paths = parts[1]

                    elif parts[0] == "MANLOCALE":
                        if debug_level > 2:
                            print("--   MANLOCALE", file=sys.stderr)
                        if len(parts) == 2:
                            if locales:
                                locales += ":" + parts[1]
                            else:
                                locales = parts[1]

                    elif line.startswith("EQN_") \
                    or line.startswith("NROFF_") \
                    or line.startswith("PIC_") \
                    or line.startswith("TBL_") \
                    or line.startswith("TROFF_") \
                    or line.startswith("REFER_") \
                    or line.startswith("VGRIND_"):
                        if len(parts) >= 2:
                            processors.append(parts[0] + "=" + " ".join(line.split()[1:]))
                            if debug_level > 2:
                                print(parts[0])
                                print("--   Parsed %s" % parts[0], file=sys.stderr)

                    elif line.startswith("#"):
                        if debug_level > 2:
                            print("--   Comment", file=sys.stderr)

    return config, paths, locales, processors


################################################################################
def read_man_conf_files(debug_level = 0):
    """Return man(1) and manpath(1) configuration files data"""
    manconfig = ""
    manpaths = ""
    manlocales = ""
    manprocessors = []

    if os.path.isdir("/etc"):
        manconfig, manpaths, manlocales, manprocessors = _read_configuration_file(
            "/etc/man.conf", debug_level
        )
    else:
        dir_list = libpnu.locate_directory("etc")
        for directory in dir_list:
            if os.path.isfile(directory + os.sep + "man.conf"):
                manconfig, manpaths, manlocales, manprocessors = _read_configuration_file(
                    directory + os.sep + "man.conf", debug_level
                )
                break

    directory = ""
    extension = ""
    if manconfig:
        if os.sep in manconfig:
            directory = manconfig.split(os.sep + "*")[0]
            extension = manconfig.split(os.sep + "*")[1]
        elif os.altsep in manconfig:
            directory = manconfig.split(os.altsep + "*")[0]
            extension = manconfig.split(os.altsep + "*")[1]
        else:
            directory = "."
            extension = manconfig.split("*")[1]
    else:
        manconfig = "/usr/local/etc/man.d/*.conf"
        directory = "/usr/local/etc/man.d"
        extension = ".conf"
    if not os.path.isdir(directory):
        dir_list = libpnu.locate_directory(directory)
        if dir_list:
            directory = dir_list[0]

    if directory:
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith(extension):
                    _, paths, locales, processors = _read_configuration_file(
                        root + os.sep + file, debug_level
                    )
                    if paths:
                        if manpaths:
                            manpaths += ":" + paths
                        else:
                            manpaths = paths
                    if locales:
                        if manlocales:
                            manlocales += ":" + locales
                        else:
                            manlocales = locales
                    if processors:
                        manprocessors += processors
            break

    return manpaths, manlocales, manprocessors


if __name__ == "__main__":
    sys.exit(0)
