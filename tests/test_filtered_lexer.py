from __future__ import print_function

from phply import phplex

import nose.tools
import pprint

def eq_tokens(input, expected, ignore=('WHITESPACE', 'OPEN_TAG', 'CLOSE_TAG')):
    output = []
    lexer = phplex.lexer.clone()
    lexer.input(input)

    while True:
        tok = lexer.token()
        if not tok: break
        if tok.type in ignore: continue
        output.append((tok.type, tok.value))

    print('Lexer output:')
    pprint.pprint(output)
    print()

    print('Token by token:')
    for out, exp in zip(output, expected):
        print('\tgot:', out, '\texpected:', exp)
        nose.tools.eq_(out, exp)

    assert len(output) == len(expected), \
           'output length was %d, expected %s' % (len(output), len(expected))

def test_close_open_tags():
    # ?><?php should be interpreted as a semi-colon
    input = '<?php if (1): if (2) 3; ?><?php else: 0; endif;'
    expected = [
        ('IF', 'if'),
        ('LPAREN', '('),
        ('LNUMBER', '1'),
        ('RPAREN', ')'),
        ('COLON', ':'),
        ('IF', 'if'),
        ('LPAREN', '('),
        ('LNUMBER', '2'),
        ('RPAREN', ')'),
        ('LNUMBER', '3'),
        ('SEMI', ';'),
        ('SEMI', ';'),
        ('ELSE', 'else'),
        ('COLON', ':'),
        ('LNUMBER', '0'),
        ('SEMI', ';'),
        ('ENDIF', 'endif'),
        ('SEMI', ';')
    ]
    eq_tokens(input, expected)
