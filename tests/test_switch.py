#!/usr/bin/env python

# php2python.py - Converts PHP to Python using unparse.py
# Usage: php2python.py < input.php > output.py

import sys
sys.path.append('..')
from phply import phpast as php
from phply.phplex import lexer
from phply.phpparse import parser
from phply import pythonast

from tools.unparse import Unparser
import os

res_path = os.path.join(os.path.pardir, "res")
files = os.listdir(res_path)

if not os.path.isdir("res-out"):
    os.mkdir("res-out")

out_dir = os.path.join(os.curdir, "res-out")

for index, the_file in enumerate(files):
    print("Testing {}".format(the_file))
    input = open(os.path.join(res_path, the_file), 'rb')
    # Make an output file with the same name but appended with -python.py
    output = open("{}-python.py".format(os.path.join(out_dir, the_file)), 'wb')

    body = []
    for ast in parser.parse(input.read(), lexer=lexer):
        if isinstance(ast, php.Switch):
            switch = pythonast.PySwitch()
            body.extend(switch.process(ast))
        else:
            body.append(pythonast.from_phpast(ast))

    Unparser(body, output)
