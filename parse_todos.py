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

statements = ["TODO", "FIXME"]
filetypes = [ {"endings": (".f90"), "commentChars": ("!"), "type": "free-form Fortran"},
              {"endings": (".tex"), "commentChars": ("%"), "type": "LaTeX"},
              {"endings": (".py", ".pyx"), "commentChars": ("#"), "type": "Python/Cython"},
              {"endings": (".c", ".h", ".cpp", ".hpp"), "commentChars": ("//", "/*"), "type": "C/C++"}
            ]
whitespaceChars = [ " ", "\t"]

_linesChecked = 0
_todoLines = 0


def findTODOs(fileName):
    """Find comments in file 'fileName' and write them to the terminal.
    """

    numOfTODOs = 0
    global _linesChecked

    # try to open the file:
    try:
        fileObj = open(fileName, mode="r")
    except:
        print("Could not open file %s."%fileName)
        return numOfTODOs

    #print "openend %s"%fileName

    # determine filetype by ending:
    foundType = False
    for i in range(len(filetypes)): # iterate till ending is found
        if(fileName.endswith(filetypes[i]["endings"])):
            #print("File %s is of type %s."%(fileName, filetypes[i]["type"]))
            fTypeIndex = i
            foundType = True
    if(not foundType):
        if(options.verbose):
            print("File %s is not of known type."%fileName)
        return numOfTODOs

    lines = fileObj.readlines()
    fileObj.close()

    # find comments:
    for i in range(len(lines)):
        _linesChecked += 1
        # check if line contains a comment and TODO-like thing
        for commentStatement in statements:
            if(commentStatement in lines[i]):
                # check if the comment statements appears *after* a comment character:
                for commentChar in filetypes[fTypeIndex]["commentChars"]:
                    if((lines[i].rfind(commentStatement) > lines[i].rfind(commentChar)) and (lines[i].rfind(commentChar) >= 0)):
                        printTODOline(fileName, i+1, lines[i])
                        numOfTODOs += 1

    return numOfTODOs


def printTODOline(fileName, lineNumber, line):
    """Print a line containing a TODO-like statement.

    All formatting has to appear here. Leading white space is stripped.
    """

    # find position of first non white-space character:
    i = len(line) - len(line.lstrip())

    print("* %s, line %s: %s"%(fileName, lineNumber, line[i:-1]))  # strip newline


def listOfVCfiles():
    """Return a list of all files that are under version control.

    Currently supported: git and svn.

    The current directory is used.
    """

    failureStrings = {"git": "Not a git repository",
                      "svn": "is not a working copy"}

    # try git first:
    output = os.popen("git ls-files")
    outputLines = output.readlines()
    if(len(outputLines) > 0):
        if(outputLines[0].rfind(failureStrings["git"]) == -1):  # directory is a git repo:
            fileList = []
            for fileName in outputLines:
                fileList.append(fileName[:-1])  # remove \n
            return fileList

    # try svn:
    output = os.popen("svn ls")
    outputLines = output.readlines()
    if(len(outputLines) > 0):
        if(outputLines[0].rfind(failureStrings["git"]) == -1):  # directory is a svn repo:
            fileList = []
            for fileName in outputLines:
                fileList.append(fileName[:-1])  # remove \n
            return fileList

    # TODO: figure out how to use the subprocess module such that STDERR is not shown in terminal

    # catch unsuccessful case:
    print("Directory appears to be neither a git nor svn repository!")
    return []

if(__name__ == "__main__"):

    # define options for OptionParser:
    progUsage = "usage: %prog file1 file2"
    parser = OptionParser(usage=progUsage)
    parser.add_option("-c", "--vc", action="store_true", default=False,
                      dest="useVC", help="Use list of files under version control (git/svn).")
    parser.add_option("-v", "--verbose", action="store_true", default=False,
                      dest="verbose", help="Be verbose -- mention files of unknown type.")
    (options, args) = parser.parse_args()

    # decide what to do:
    # if --vc is given, go through the files under version control first:
    if(options.useVC):
        filesToAppend = listOfVCfiles()
        if(len(filesToAppend) > 0):
            for newFile in filesToAppend:
                args.append(newFile)

    if(len(args) == 0):
        parser.error("No files specified.")

    # go through all files given as an arguments to the script:
    for fileName in args:
        number = findTODOs(fileName)
        _todoLines += number
        if(number > 0):
            print("")  # print a newline after each file processed

    print("%s lines checked in total, %s TODO-like statements found."\
          %(_linesChecked, _todoLines))
