#!/usr/bin/env python

# php2python.py - Converts PHP to Python using codegen.py
# Usage: php2python.py < input.php > output.py

import sys
sys.path.append('..')

from phply.phpparse import parser
from phply import pythonast

from ast import Module
import codegen

input = sys.stdin
output = sys.stdout

body = [pythonast.from_phpast(ast) for ast in parser.parse(input.read())]
output.write(codegen.to_source(Module(body)))
output.write('\n')
