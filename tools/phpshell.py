#!/usr/bin/env python

# phpshell.py - PHP interactive interpreter

import sys
sys.path.append('..')

import ast
import pprint
import readline
import traceback

from phply import pythonast, phplex
from phply.phpparse import make_parser

def echo(*objs):
    for obj in objs:
        sys.stdout.write(str(obj))

def inline_html(obj):
    sys.stdout.write(obj)

def XXX(obj):
    print('Not implemented:\n ', obj)

def ast_dump(code):
    print('AST dump:')
    print(' ', ast.dump(code, include_attributes=True))

def php_eval(nodes):
    body = []
    for node in nodes:
        stmt = pythonast.to_stmt(pythonast.from_phpast(node))
        body.append(stmt)
    code = ast.Module(body)
    # ast_dump(code)
    eval(compile(code, '<string>', mode='exec'), globals())

parser = make_parser()

s = ''
lexer = phplex.lexer
parser.parse('<?', lexer=lexer)

while True:
   if s:
       prompt = '     '
   else:
       prompt = lexer.current_state()
       if prompt == 'INITIAL': prompt = 'html'
       prompt += '> '

   try:
       s += input(prompt)
   except EOFError:
       break

   if not s: continue
   s += '\n'

   # Catch all exceptions and print tracebacks.
   try:
       # Try parsing the input normally.
       try:
           lexer.lineno = 1
           result = parser.parse(s, lexer=lexer)
           php_eval(result)
       except SyntaxError as e:
           # Parsing failed. See if it can be parsed as an expression.
           try:
               lexer.lineno = 1
               result = parser.parse('print ' + s + ';', lexer=lexer)
               php_eval(result)
           except (SyntaxError, TypeError):
               # That also failed. Try adding a semicolon.
               try:
                   lexer.lineno = 1
                   result = parser.parse(s + ';', lexer=lexer)
                   php_eval(result)
               except SyntaxError:
                   # Did we get an EOF? If so, we're still waiting for input.
                   # If not, it's a syntax error for sure.
                   if e.lineno is None:
                       continue
                   else:
                       print(e, 'near', repr(e.text))
                       s = ''
   except:
       traceback.print_exc()

   s = ''
