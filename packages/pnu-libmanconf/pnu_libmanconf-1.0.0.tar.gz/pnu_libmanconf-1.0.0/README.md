# Installation
pip install [pnu-libmanconf](https://pypi.org/project/pnu-libmanconf/)

# LIBMANCONF(3)

## NAME
libmanconf — library for handling man(1) and manpath(1) configuration files

## SYNOPSIS
import **libmanconf**

String, String, List *libmanconf*.**read_man_conf_files**(Integer *debug_level* = 0)

## DESCRIPTION
The **read_man_conf_files()** function reads the configuration files located at "/etc/man.conf" and "/usr/local/etc/man.d/\*.conf"
to configure the manual search path, locales and utility set used by man(1) and related utilities.

The function takes an optional argument *debug_level* with an integer value from 0 (default) to 3,
to print increasingly detailed information on standard error output.

It returns a triplet consisting of:
* a string containing colon separated existing MANPATH directories
* a string containing colon separated locales (for example, "fr_FR.UTF-8:ja_JP.eucJP")
* a list containing processors (for example, \["TBL_JA=/usr/local/bin/gtbl", "NROFF_JA=/usr/local/bin/groff -man -dlang=ja_JP.eucJP"\])

## SEE ALSO
[apropos(1)](https://www.freebsd.org/cgi/man.cgi?query=apropos&sektion=1),
[man(1)](https://www.freebsd.org/cgi/man.cgi?query=man&sektion=1),
[man.conf(5)](https://www.freebsd.org/cgi/man.cgi?query=man.conf&sektion=5),
[manpath(1)](https://www.freebsd.org/cgi/man.cgi?query=manpath&sektion=1),
[whatis(1)](https://www.freebsd.org/cgi/man.cgi?query=whatis&sektion=1)

## STANDARDS
The **libmanconf** library is not a standard UNIX one.

It tries to follow the [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide for [Python](https://www.python.org/) code.

## PORTABILITY
To be tested under Windows.

## HISTORY
This library was made for the [PNU project](https://github.com/HubTou/PNU) to factor code for the man(1) and manpath(1) commands.

## LICENSE
It is available under the [3-clause BSD license](https://opensource.org/licenses/BSD-3-Clause).

## AUTHORS
[Hubert Tournier](https://github.com/HubTou)

The man.conf(5) manual page is largely based on the one written for [FreeBSD](https://www.freebsd.org/) by [Gordon Tetlow](https://github.com/tetlowgm).

