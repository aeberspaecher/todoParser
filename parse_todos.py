#!/usr/bin/env python
#-*- coding:utf-8 -*-

#  Copyright 2012-2013 Alexander Eberspächer <alex(dot)eberspaecher(at)googlemail.com>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.

"""A little script to parse TODO-like statements in source files.

The script parses all (supported) source files in a given path, tries to read
"TODO: do this and that"-like comments and writes these commands to the
terminal.

Source formats supported so far:

*.f90: free-form Fortran 90
*.c, *.h, *.cpp, *.hpp, *.cxx, *.hxx: C/C++
*.py: Python
*.pyx, *.pxd, *.pxi: Cython
*.tex: LaTeX
*.m: Matlab
"""

# to add new filetypes or TODO-like statements, add to the lists 'statements' and 'filetypes'

import os
import os.path
import sys
from optparse import OptionParser
from subprocess import Popen, PIPE

statements = ("TODO", "FIXME")
filetypes = ( {"endings": (".f90"), "comment_chars": ("!"), "type": "free-form Fortran"},
              {"endings": (".tex"), "comment_chars": ("%"), "type": "LaTeX"},
              {"endings": (".py", ".pyx", "*.pxi"), "comment_chars": ("#"), "type": "Python/Cython"},
              {"endings": (".c", ".h", ".cpp", ".hpp"), "comment_chars": ("//", "/*"), "type": "C/C++"},
              {"endings": (".m"), "comment_chars": ("%"), "type": "Matlab"},
            )
whitespace_chars = (" ", "\t")


def get_dir(path):
    """Get absolute directory of path, no matter if path points to a file,
    a directory, is absolute or relative.
    """

    abspath = os.path.abspath(path)
    if not os.path.isdir(abspath):
        abs_dir = os.path.dirname(abspath)
    else:
        abs_dir = abspath

    return abs_dir


def is_git_repo(path):
    """Checks if path is in a git repository.
    """

    base_path = os.path.realpath(path)
    sub_path = ""

    is_repo = True

    while not os.path.exists(os.path.join(base_path, ".git")):
        # ascend in directory hierarchy if possible
        base_path, new_sub_dir = os.path.split(base_path)
        sub_path = os.path.join(new_sub_dir, sub_path)
        # root directory reached? -> not in Git repo
        if new_sub_dir == "":
            is_repo = False
            break

    return is_repo


def is_svn_repo(path):
    """Like is_git_repo(), but for SVN repos.
    """

    base_path = os.path.realpath(path)

    return True if os.path.exists(os.path.join(base_path, ".svn")) else False


def check_filetype(filename):
    """Check for filetype by checking the file extension. If the file has a
    known extension, return a dictionary providing information on the comment
    characters of the file type.
    """

    for filetype in filetypes:  # iterate till ending is found
        if(filename.endswith(filetype["endings"])):
            return filetype

    # if filetype is unknown, this is reached:
    return None


def count_and_print_todos(filename, filetype):
    """Parse a file for TODO-like statements. Print all found statements and
    return number of hits.

    Parameters
    ----------
    filename : string
    filetype : dict
        Has to provide information on the comment character used by the file
        type via entry "comment_chars".

    Returns
    -------
    lines_checked: int
        Number of lines checked.
    num_todos : int
        Number of TODOs found.
    """

    comment_chars = filetype["comment_chars"]
    lines_checked = 0
    num_todos = 0

    try:
        file_obj = open(filename, "r")
    except IOError:
        print("Could not open file %s"%filename)
    else:
        with file_obj:
            lines = file_obj.readlines()

    for j, line in enumerate(lines):
        lines_checked += 1
        # check if line contains a comment and TODO-like thing
        for comment_statement in statements:
            if(comment_statement in line):
                # check if the comment statements appears *after* a comment character:
                for comment_char in comment_chars:
                    if((line.rfind(comment_statement) > line.rfind(comment_char)) and (line.rfind(comment_char) >= 0)):
                        print_todo_line(filename, j+1, line)
                        num_todos += 1

    return lines_checked, num_todos


def find_todos(filename):
    """Find comments in file 'filename' and write them to the terminal.

    Parameters
    ----------
    filename : string

    Returns
    -------
    lines_checked: int
        Number of lines checked.
    num_todos : int
        Number of TODOs found.
    """

    file_type = check_filetype(filename)
    if(file_type is None):
        if(options.verbose):
            print("File %s is not of known type."%filename)
        return 0, 0

    lines_checked, num_todos = count_and_print_todos(filename, file_type)

    return lines_checked, num_todos


def print_todo_line(filename, line_number, line):
    """Print a line containing a TODO-like statement.

    All formatting has to be done here. Leading white space is stripped.

    Parameters
    ----------
    filename : string
    line_number : int
    line : string
    """

    # find position of first non white-space character:
    i = len(line) - len(line.lstrip())

    print("* %s, line %s: %s"%(filename, line_number, line[i:-1]))  # strip newline


def vc_files(path):
    """Return a list of all files that are under version control.

    Currently supported: git and svn.

    Parameters
    ----------
    path : string
        Path that containing a git or svn repository.
    """

    def get_files_from_string_list(string):
        """Return a list of absolute path to files from string containing
        a string of relative filenames separated by new lines.
        """

        file_list = string.split("\n")
        res_list = []
        # prepend all list elements with path as the version control tools output relative paths!
        for f in file_list:
            res_list.append(os.path.join(path, f))

        return res_list

    file_list = []

    if(is_git_repo(path)):
        try:
            proc = Popen(["git", "ls-files"], stdout=PIPE, stderr=PIPE, cwd=path)
            result = proc.stdout.read()
            file_list = get_files_from_string_list(result)
        except OSError:  # git error
            print >> sys.stderr, "Something wrong while executing 'git ls-files'"
        return file_list
    elif(is_svn_repo(path)):
        try:
            proc = Popen(["svn", "ls"], stdout=PIPE, stderr=PIPE, cwd=path)
            result = proc.stdout.read()
            file_list = get_files_from_string_list(result)
        except OSError:
            print >> sys.stderr, "Something wrong while executing 'svn ls'"
        return file_list
    else:  # catch unsuccessful case:
        print >> sys.stderr, "Directory appears to be neither a git nor svn repository!"
        return []


if(__name__ == "__main__"):
    lines_checked = 0
    todo_lines = 0

    # define options for OptionParser:
    prog_usage = "usage: %prog file1 file2"
    parser = OptionParser(usage=prog_usage)
    parser.add_option("-c", "--vc", action="store_true", default=False,
                      dest="useVC", help="Use list of files under version control (git/svn).")
    parser.add_option("-v", "--verbose", action="store_true", default=False,
                      dest="verbose", help="Be verbose -- mention files of unknown type.")
    (options, args) = parser.parse_args()

    # decide what to do:
    # if --vc is given, go through the files under version control first:
    if(options.useVC):
        if(len(args) == 0):
            args = [os.environ["PWD"]]
        files = []
        for arg in args:
            files += vc_files(get_dir(arg))
        if(len(files) > 0):
            for new_file in files:
                args.append(new_file)

    if(len(args) == 0):
        parser.error("No files specified.")

    # go through all files given as an arguments to the script:
    for filename in args:
        lines, todos = find_todos(filename)
        lines_checked += lines
        todo_lines += todos

        if(todos > 0):
            print("")  # print a newline after each file processed

    print("%s lines checked in total, %s TODO-like statements found."
          %(lines_checked, todo_lines))
