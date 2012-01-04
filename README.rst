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

- Python/Cython
- free-form Fortran
- LaTeX

Usage
=====

Use the parser according to::

  ./todoParser file1 file2

Known annoyances
================

The parser will ignore TODOs inside strings. This may be undesired behaviour
in eg. Python docstrings.

License
=======

todoParser is distributed under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2 of the
License, or (at your option) any later version.  A copy of this license can
be found in the file COPYING included with the source code of this program.

2012 by Alexander Eberspächer
