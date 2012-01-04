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

from optparse import OptionParser

statements = ["TODO", "FIXME"]
filetypes = [ {"endings": (".f90"), "commentChars": ("!"), "type": "free-form Fortran"},
              {"endings": (".tex"), "commentChars": ("%"), "type": "LaTeX"},
              {"endings": (".py", ".pyx"), "commentChars": ("#"), "type": "Python/Cython"}
            ]


progUsage = "usage: %prog file"
parser = OptionParser(usage=progUsage)
(options, args) = parser.parse_args()

def findComments(fileName):
    """Find comments in file 'fileName' and write them to the terminal.
    """

    # try to open the file:
    try:
        fileObj = open(fileName, mode="r")
    except:
        print("Could not open file %s."%fileName)
        return

    # determine filetype by ending:
    for i in range(len(filetypes)): # iterate till ending is found
        if(fileName.endswith(filetypes[i]["endings"])):
            print("File %s is of type %s."%(fileName, filetypes[i]["type"]))
            fTypeIndex = i
            exit
        if(i == len(filetypes)):
            print("File %s is not of known type."%fileName)
            return

    lines = fileObj.readlines()
    fileObj.close()

    # find comments:
    for i in range(len(lines)):
        # check if line contains a comment and TODO-like thing
        for commentStatement in statements:
            if(commentStatement in lines[i]):
                # check if the comment statements appears *after* a comment character:
                for commentChar in filetypes[fTypeIndex]["commentChars"]:
                    if((lines[i].rfind(commentStatement) > lines[i].rfind(commentChar)) and (lines[i].rfind(commentChar) >= 0)):
                        print("* %s, line %s: %s"%(fileName, i+1, lines[i]))

                # TODO: possibly include multi-line TODOs as well


# TODO: implement parsing of "git ls-files"

if(__name__ == "__main__"):
    # go through all files given as an arguments to the script:
    for fileName in args:
        findComments(fileName)
