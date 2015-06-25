#!/usr/bin/env python

# php2python.py - Converts PHP to Python using unparse.py
# Usage: php2python.py < input.php > output.py

import sys
import argparse
sys.path.append('..')
from phply import phpast as php
from phply.phplex import lexer
from phply.phpparse import parser
from phply import pythonast

from ast import Module
from unparse import Unparser

parser2 = argparse.ArgumentParser()
parser2.add_argument("the_input")
parser2.add_argument("the_output")
args = parser2.parse_args()

# input = sys.stdin
# output = sys.stdout

input = open(args.the_input, 'rb')
output = open(args.the_output, 'wb')

body = []
for ast in parser.parse(input.read(), lexer=lexer):
    ast_return = pythonast.from_phpast(ast)
    if isinstance(ast_return, list):
        body.extend(ast_return)
    else:
        body.append(ast_return)

if pythonast.needs_strpos:
    body.append(pythonast.py_strpos_ast)
Unparser(body, output)
