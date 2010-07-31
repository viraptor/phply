from phply.phpparse import parser
from phply.phpast import *
import nose.tools

def eq_ast(input, expected):
    output = parser.parse(input)
    print output
    assert len(output) == len(expected)
    for out, exp in zip(output, expected):
        print out, exp
        nose.tools.eq_(out, exp)

def test_inline_html():
    input = 'html <?php // php ?> more html'
    expected = [InlineHTML('html '), InlineHTML(' more html')]
    eq_ast(input, expected)

def test_echo():
    input = '<?php echo "hello, world!"; ?>'
    expected = [Echo(["hello, world!"])]
    eq_ast(input, expected)

def test_exit():
    input = '<?php exit; exit(); exit(123); die; die(); die(456); ?>'
    expected = [
        Exit(None), Exit(None), Exit(123),
        Exit(None), Exit(None), Exit(456),
    ]
    eq_ast(input, expected)

def test_unary_ops():
    input = r"""<?
        $a = -5;
        $b = +6;
        $c = !$d;
        $e = ~$f;
    ?>"""
    expected = [
        Assignment(Variable('$a'), UnaryOp('-', 5), False),
        Assignment(Variable('$b'), UnaryOp('+', 6), False),
        Assignment(Variable('$c'), UnaryOp('!', Variable('$d')), False),
        Assignment(Variable('$e'), UnaryOp('~', Variable('$f')), False),
    ]
    eq_ast(input, expected)

def test_assignment_ops():
    input = r"""<?
        $a += 5;
        $b -= 6;
        $c .= $d;
        $e ^= $f;
    ?>"""
    expected = [
        AssignOp('+=', Variable('$a'), 5),
        AssignOp('-=', Variable('$b'), 6),
        AssignOp('.=', Variable('$c'), Variable('$d')),
        AssignOp('^=', Variable('$e'), Variable('$f')),
    ]
    eq_ast(input, expected)

# def test_variable_variables():
    # input = r"""<?
        # $$a = $$b;
        # $$a =& $$b;
        # ${$a} = ${$b};
        # ${$a} =& ${$b};
    # ?>"""
    # expected = [
        # Assignment(Variable(Variable('$a')), Variable(Variable('$b')), False),
        # Assignment(Variable(Variable('$a')), Variable(Variable('$b')), True),
        # Assignment(Variable(Variable('$a')), Variable(Variable('$b')), False),
        # Assignment(Variable(Variable('$a')), Variable(Variable('$b')), True),
    # ]
    # eq_ast(input, expected)
