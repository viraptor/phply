#!/usr/bin/env python

# php2json.py - Converts PHP to a JSON-based abstract syntax tree
# Usage: php2json.py < input.php > output.json

import sys
sys.path.append('..')

from phply.phplex import lexer
from phply.phpparse import make_parser

import simplejson

input = sys.stdin
output = sys.stdout
with_lineno = True

def export(items):
    result = []
    if items:
       for item in items:
           if hasattr(item, 'generic'):
               item = item.generic(with_lineno=with_lineno)
           result.append(item)
    return result

parser = make_parser()
simplejson.dump(export(parser.parse(input.read(),
                                    lexer=lexer,
                                    tracking=with_lineno)),
                output, indent=2)
output.write('\n')
