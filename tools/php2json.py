#!/usr/bin/env python

# php2json.py - Converts PHP to a JSON-based abstract syntax tree
# Usage: php2json.py < input.php > output.json

import sys
sys.path.append('..')

from phply.phpparse import parser
import simplejson

input = sys.stdin
output = sys.stdout

def export(items):
    result = []
    if items:
       for item in items:
           if hasattr(item, 'generic'):
               item = item.generic()
           result.append(item)
    return result

simplejson.dump(export(parser.parse(input.read())), output, indent=2)
output.write('\n')
