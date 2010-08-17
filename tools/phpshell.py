#!/usr/bin/env python

# phpshell.py - PHP interactive interpreter

import sys
sys.path.append('..')

import ast
import pprint
import readline
import traceback

from phply import pythonast, phplex
from phply.phpparse import parser

def echo(obj):
    sys.stdout.write(str(obj))

inline_html = echo

def XXX(obj):
    print 'Not implemented:', obj

def ast_dump(code):
    print 'AST dump:'
    print ' ', ast.dump(code, include_attributes=True)

def php_eval(nodes):
    body = []
    for node in nodes:
        stmt = pythonast.to_stmt(pythonast.from_phpast(node))
        # if not isinstance(stmt, ast.stmt):
            # stmt = ast.Expr(stmt, lineno=stmt.lineno, col_offset=0)
        body.append(stmt)
    code = ast.Module(body)
    ast_dump(code)
    eval(compile(ast.parse(code), '<string>', mode='exec'), globals())

s = ''
lexer = phplex.lexer
while True:
   try:
       s += raw_input('     ' if s else 'php> ')
   except EOFError:
       break
   if not s: continue
   s += '\n'
   try:
       lexer.lineno = 1
       result = parser.parse(s, lexer=lexer)
   except SyntaxError, e:
       if e.lineno is not None:
           print e, 'near', repr(e.text)
           s = ''
       continue
   if result:
       try:
           php_eval(result)
       except:
           traceback.print_exc()
   s = ''
