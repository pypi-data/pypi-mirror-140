# Copyright 2021 Casey Devet
#
# Permission is hereby granted, free of charge, to any person obtaining a 
# copy of this software and associated documentation files (the "Software"), 
# to deal in the Software without restriction, including without limitation 
# the rights to use, copy, modify, merge, publish, distribute, sublicense, 
# and/or sell copies of the Software, and to permit persons to whom the 
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included 
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS 
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL 
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING 
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER 
# DEALINGS IN THE SOFTWARE.

# This module provides some useful functions that make
# teaching Python a bit easier.  To make these functions 
# available in your program, import them using the command:
# from easyio import *

import os
import sys


# This function can be used to show an error message in the 
# console, then end the program.
def error (message, status=0):
    '''
    Print an error message to the console and and the program.
    '''
    
    print(f"\n{message}\n", file=sys.stderr)
    sys.exit(status)


# This variable holds the built-in input() function that we
# are replacing
py_input = input


# This function can be used to get input from the console or 
# from another source (like a file).  It can also convert an
# input value to a certain type before returning it.  If this
# module is imported with "import *", then this function will
# replace the built-in input() function.
def input (prompt=None, source=None, type=str):
    '''
    Read a line of input.

    The prompt string, if given, is printed to the console 
    before reading input.

    The input value can be converted to any type using the type
    parameter.  This needs to be a function that takes a string
    and converts it to the desired type (e.g. int, float, number,
    etc.)

    The source can be any file-like object that has a .readline()
    method.  By default the source is the standard input stream
    (stuff typed into the console).
    '''

    if not callable(type):
        raise error(f"Invalid type: {type.__name__}")
    try:
        if source is None:
            string = py_input("" if prompt is None else prompt)
        else:
            string = source.readline()
    except EOFError:
        error("The source has no more data!")
    except:
        error("There was an error trying to get input!")
    try:
        return type(string)
    except ValueError:
        error(f"This input is not a valid {type.__name__}: {string}")
    except TypeError:
        error(f"Invalid type: {type.__name__}")
    except:
        error(f"There was an issue converting '{string}' to type {type.__name__}")


# This function can be used to get multiple lines of input 
# from the console or from another source (like a file).  It 
# can also convert an input value to a certain type before 
# returning it.
def inputs (prompt=None, source=None, type=str):
    '''
    Read multiple lines of input.

    The prompt string, if given, is printed to the console 
    before reading each line of input.

    The input value can be converted to any type using the type
    parameter.  This needs to be a function that takes a string
    and converts it to the desired type (e.g. int, float, number,
    etc.)

    The source can be any file-like object that has a .readline()
    method.  By default the source is the standard input stream
    (stuff typed into the console).
    '''

    while True:
        value = input(prompt, source, type)
        if value is None or value == '':
            break
        yield value


# Use this function to convert a numerical input to a number
def number (value):
    '''
    Convert to a numerical value.

    Whole numbers will be returned as int objects and decimal
    numbers will be returned as float objects.
    
    For convenience writing loops, the empty string will return None.
    '''

    if value == "":
        return None
    num = float(value)
    if num.is_integer():
        num = int(num)
    return num


# These are the functions that will be imported with "import *"
__all__ = [
    "error",
    "input",
    "inputs",
    "number"
]