#!/usr/bin/env python
#-*- coding:utf-8 -*-

#  Copyright 2012 Alexander Eberspächer <alex(dot)eberspaecher(at)googlemail.com>
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
*.py: Python
*.pyx: Cython
*.tex: LaTeX
"""

# to add new filetypes or TODO-like statements, add to the lists 'statements' and 'filetypes'

import os
from optparse import OptionParser

statements = ("TODO", "FIXME")
filetypes = ( {"endings": (".f90"), "comment_chars": ("!"), "type": "free-form Fortran"},
              {"endings": (".tex"), "comment_chars": ("%"), "type": "LaTeX"},
              {"endings": (".py", ".pyx"), "comment_chars": ("#"), "type": "Python/Cython"},
              {"endings": (".c", ".h", ".cpp", ".hpp"), "comment_chars": ("//", "/*"), "type": "C/C++"}
            )
whitespace_chars = ( " ", "\t")

_lines_checked = 0
_todo_lines = 0


def find_todos(filename):
    """Find comments in file 'filename' and write them to the terminal.
    """

    num_todos = 0
    global _lines_checked

    # try to open the file:
    try:
        file_obj = open(filename, mode="r")
    except:
        print("Could not open file %s."%filename)
        return num_todos

    #print "openend %s"%filename

    # determine filetype by ending:
    found_type = False
    for i in range(len(filetypes)): # iterate till ending is found
        if(filename.endswith(filetypes[i]["endings"])):
            #print("File %s is of type %s."%(filename, filetypes[i]["type"]))
            filetype_index = i
            found_type = True
    if(not found_type):
        if(options.verbose):
            print("File %s is not of known type."%filename)
        return num_todos

    lines = file_obj.readlines()
    file_obj.close()

    # find comments:
    for i in range(len(lines)):
        _lines_checked += 1
        # check if line contains a comment and TODO-like thing
        for comment_statement in statements:
            if(comment_statement in lines[i]):
                # check if the comment statements appears *after* a comment character:
                for comment_char in filetypes[filetype_index]["comment_chars"]:
                    if((lines[i].rfind(comment_statement) > lines[i].rfind(comment_char)) and (lines[i].rfind(comment_char) >= 0)):
                        print_todo_line(filename, i+1, lines[i])
                        num_todos += 1

    return num_todos


def print_todo_line(filename, lineNumber, line):
    """Print a line containing a TODO-like statement.

    All formatting has to appear here. Leading white space is stripped.
    """

    # find position of first non white-space character:
    i = len(line) - len(line.lstrip())

    print("* %s, line %s: %s"%(filename, lineNumber, line[i:-1]))  # strip newline


def vc_files():
    """Return a list of all files that are under version control.

    Currently supported: git and svn.

    The current directory is used.
    """

    failureStrings = {"git": "Not a git repository",
                      "svn": "is not a working copy"}

    # try git first:
    output = os.popen("git ls-files")
    output_lines = output.readlines()
    if(len(output_lines) > 0):
        if(output_lines[0].rfind(failureStrings["git"]) == -1):  # directory is a git repo:
            file_list = []
            for filename in output_lines:
                file_list.append(filename[:-1])  # remove \n
            return file_list

    # try svn:
    output = os.popen("svn ls")
    output_lines = output.readlines()
    if(len(output_lines) > 0):
        if(output_lines[0].rfind(failureStrings["git"]) == -1):  # directory is a svn repo:
            file_list = []
            for filename in output_lines:
                file_list.append(filename[:-1])  # remove \n
            return file_list

    # TODO: figure out how to use the subprocess module such that STDERR is not shown in terminal

    # catch unsuccessful case:
    print >> sys.err, "Directory appears to be neither a git nor svn repository!"
    return []


if(__name__ == "__main__"):

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
        files = vc_files()
        if(len(files) > 0):
            for new_file in files:
                args.append(new_file)

    if(len(args) == 0):
        parser.error("No files specified.")

    # go through all files given as an arguments to the script:
    for filename in args:
        number = find_todos(filename)
        _todo_lines += number
        if(number > 0):
            print("")  # print a newline after each file processed

    print("%s lines checked in total, %s TODO-like statements found."\
          %(_lines_checked, _todo_lines))