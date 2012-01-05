==========
todoParser
==========

About
=====

This small script may extract lines that contain statements like "TODO" or
"FIXME" in comments inside a source file.

todoParser is written in Python and is easily extendable.

Features
========

Filetypes supported:

- C/C++
- Python/Cython
- free-form Fortran
- LaTeX

Usage
=====

Use the parser according to::

  ./todoParser file1 file2

Supported options:

- ``--vc``: parse files under version control. Supported so far: git/svn.
- ``--verbose``: print names of file for which parsing fails due to
  unsupported filetype.

- a typical use case might be something like

  ::
    ./todoParser.py --vc > TODO

  to generate a TODO list for a project under version control.

Known annoyances
================

- The parser will ignore TODOs inside strings. This may be undesired behaviour
  in eg. Python docstrings.

- In C/C++ code, the parser fails to find TODOs of the following kind::

    i = 2 /* assign a number
             TODO: check if 2 is correct in any case */

- The script calls ``git ls-files`` respectively ``svn ls``. If these calls are
  unsuccessful, the error messages appear in the output.

License
=======

todoParser is distributed under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2 of the
License, or (at your option) any later version.  A copy of this license can
be found in the file COPYING included with the source code of this program.

2012 by Alexander Eberspächer
