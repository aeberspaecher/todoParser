===========
parse_todos
===========

About
=====

This small script may extract lines that contain statements like "TODO" or
"FIXME" in comments inside a source file.

parse_todos is written in Python and is easily extendable.

Features
========

Filetypes supported:

- C/C++
- Python/Cython
- free-form Fortran
- LaTeX

Parse files under version control. Supported:

- git
- svn

Usage
=====

Use the parser according to::

  ./parse_todos file1 file2

Supported options:

- ``--vc``: parse files under version control. Supported so far: git/svn.
- ``--verbose``: print names of files for which parsing fails due to an
  unsupported filetype.

Notes:

- a typical use case might be something like

  ::

    ./parse_todos.py --vc > TODO

  to generate a code-based TODO list for the current directory which is assumed
  to be under version control.

- you may combine the ``--vc`` option with paths::

    ./parse_todos.py --vc . ~/project1 /home/user/project2

  parses all supported files in ``.``, ``~/project1`` and
  ``/home/user/project2``.

Known annoyances
================

- The parser will ignore TODOs inside strings if the strings are part of
  code (i.e., not inside a comment). This may be undesired behaviour in eg.
  Python docstrings.

- In C/C++ code, the parser fails to find TODOs of the following kind::

    i = 2 /* assign a number
             TODO: check if 2 is correct in any case */

- The script calls ``git ls-files`` respectively ``svn ls``. If these calls are
  unsuccessful, the error messages appear in the output.

License
=======

parse_todos is distributed under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2 of the
License, or (at your option) any later version.  A copy of this license can
be found in the file COPYING included with the source code of this program.

© 2012-2014 by Alexander Eberspächer
