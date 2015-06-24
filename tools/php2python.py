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
    if isinstance(ast, php.Switch):
        switch = pythonast.PySwitch()
        body.extend(switch.process(ast))
    else:
        body.append(pythonast.from_phpast(ast))

Unparser(body, output)
