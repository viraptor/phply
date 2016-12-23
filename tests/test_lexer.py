from __future__ import print_function

from phply import phplex

import nose.tools
import pprint

def eq_tokens(input, expected, ignore=('WHITESPACE', 'OPEN_TAG', 'CLOSE_TAG')):
    output = []
    lexer = phplex.full_lexer.clone()
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

def test_whitespace():
    input = ' <?  \t\r\n ?>\t\t <?php  ?> <?php\n ?>'
    expected = [
        ('INLINE_HTML', ' '),
        ('OPEN_TAG', '<?'),
        ('WHITESPACE', '  \t\r\n '),
        ('CLOSE_TAG', '?>'),
        ('INLINE_HTML', '\t\t '),
        ('OPEN_TAG', '<?php '),
        ('WHITESPACE', ' '),
        ('CLOSE_TAG', '?>'),
        ('INLINE_HTML', ' '),
        ('OPEN_TAG', '<?php\n'),
        ('WHITESPACE', ' '),
        ('CLOSE_TAG', '?>'),
    ]
    eq_tokens(input, expected, ignore=())

def test_open_close_tags():
    input = '<? ?> <% %> <?php ?> <?= ?> <%= %>'
    expected = [
        ('OPEN_TAG', '<?'),
        ('WHITESPACE', ' '),
        ('CLOSE_TAG', '?>'),
        ('INLINE_HTML', ' '),
        ('OPEN_TAG', '<%'),
        ('WHITESPACE', ' '),
        ('CLOSE_TAG', '%>'),
        ('INLINE_HTML', ' '),
        ('OPEN_TAG', '<?php '),
        ('CLOSE_TAG', '?>'),
        ('INLINE_HTML', ' '),
        ('OPEN_TAG_WITH_ECHO', '<?='),
        ('WHITESPACE', ' '),
        ('CLOSE_TAG', '?>'),
        ('INLINE_HTML', ' '),
        ('OPEN_TAG_WITH_ECHO', '<%='),
        ('WHITESPACE', ' '),
        ('CLOSE_TAG', '%>'),
    ]
    eq_tokens(input, expected, ignore=())

def test_numbers():
    input = """<?
        0
        12
        34.56
        7e8
        9.01e23
        4.5E+6
        .78e-9
        1.e+2
        34.
        .56
        0xdEcAfBaD
        0x123456789abcdef
        0666
    ?>"""
    expected = [
        ('LNUMBER', '0'),
        ('LNUMBER', '12'),
        ('DNUMBER', '34.56'),
        ('DNUMBER', '7e8'),
        ('DNUMBER', '9.01e23'),
        ('DNUMBER', '4.5E+6'),
        ('DNUMBER', '.78e-9'),
        ('DNUMBER', '1.e+2'),
        ('DNUMBER', '34.'),
        ('DNUMBER', '.56'),
        ('LNUMBER', '0xdEcAfBaD'),
        ('LNUMBER', '0x123456789abcdef'),
        ('LNUMBER', '0666'),
    ]
    eq_tokens(input, expected)

def test_strings():
    input = r"""<?
        ''
        'hello'
        'what\'s up'
        'newlines
'
        ""
        "hello"
        "$world"
        "hello $cruel \"world\""
        "end$"
        "newlines
"
    ?>"""
    expected = [
        ('CONSTANT_ENCAPSED_STRING', "''"),
        ('CONSTANT_ENCAPSED_STRING', "'hello'"),
        ('CONSTANT_ENCAPSED_STRING', "'what\\'s up'"),
        ('CONSTANT_ENCAPSED_STRING', "'newlines\n'"),
        ('QUOTE', '"'), ('QUOTE', '"'),
        ('QUOTE', '"'), ('ENCAPSED_AND_WHITESPACE', 'hello'), ('QUOTE', '"'),
        ('QUOTE', '"'), ('VARIABLE', '$world'), ('QUOTE', '"'),
        ('QUOTE', '"'), ('ENCAPSED_AND_WHITESPACE', 'hello '),
        ('VARIABLE', '$cruel'), ('ENCAPSED_AND_WHITESPACE', ' \\"world\\"'), ('QUOTE', '"'),
        ('QUOTE', '"'), ('ENCAPSED_AND_WHITESPACE', 'end$'), ('QUOTE', '"'),
        ('QUOTE', '"'), ('ENCAPSED_AND_WHITESPACE', 'newlines\n'), ('QUOTE', '"'),
    ]
    eq_tokens(input, expected)

def test_string_backslash_escapes():
    input = r"""<?
    "
        \$escape
        \{$escape}
        \${escape}
    "
    ?>"""
    expected = [
        ('QUOTE', '"'),
        ('ENCAPSED_AND_WHITESPACE', "\n        \\$escape\n        \\{"),
        ('VARIABLE', "$escape"),
        ('ENCAPSED_AND_WHITESPACE', "}\n        \\${escape}\n    "),
        ('QUOTE', '"'),
    ]
    eq_tokens(input, expected)

def test_string_offset_lookups():
    input = r"""<?
    "
        $array[offset]
        $too[many][offsets]
        $next[to]$array
        ${curly['offset']}
        $object->property
        $too->many->properties
        $adjacent->object$lookup
        stray -> [ ]
        not[array]
        non->object
    "
    ?>"""
    expected = [
        ('QUOTE', '"'),
        ('ENCAPSED_AND_WHITESPACE', '\n        '),
        ('VARIABLE', '$array'), ('LBRACKET', '['), ('STRING', 'offset'), ('RBRACKET', ']'),
        ('ENCAPSED_AND_WHITESPACE', '\n        '),
        ('VARIABLE', '$too'), ('LBRACKET', '['), ('STRING', 'many'), ('RBRACKET', ']'),
        ('ENCAPSED_AND_WHITESPACE', '[offsets]\n        '),
        ('VARIABLE', '$next'), ('LBRACKET', '['), ('STRING', 'to'), ('RBRACKET', ']'),
        ('VARIABLE', '$array'), ('ENCAPSED_AND_WHITESPACE', '\n        '),
        ('DOLLAR_OPEN_CURLY_BRACES', '${'), ('STRING_VARNAME', 'curly'),
        ('LBRACKET', '['), ('CONSTANT_ENCAPSED_STRING', "'offset'"), ('RBRACKET', ']'),
        ('RBRACE', '}'), ('ENCAPSED_AND_WHITESPACE', '\n        '),
        ('VARIABLE', '$object'), ('OBJECT_OPERATOR', '->'), ('STRING', 'property'),
        ('ENCAPSED_AND_WHITESPACE', '\n        '),
        ('VARIABLE', '$too'), ('OBJECT_OPERATOR', '->'), ('STRING', 'many'),
        ('ENCAPSED_AND_WHITESPACE', '->properties\n        '),
        ('VARIABLE', '$adjacent'), ('OBJECT_OPERATOR', '->'), ('STRING', 'object'),
        ('VARIABLE', '$lookup'),
        ('ENCAPSED_AND_WHITESPACE', '\n        stray -> [ ]\n        not[array]\n        non->object\n    '),
        ('QUOTE', '"'),
    ]
    eq_tokens(input, expected)

def test_string_curly_dollar_expressions():
    input = r"""<?
    "
        a${dollar_curly}b
        c{$curly_dollar}d
        e${$dollar_curly_dollar}f
        {$array[0][1]}
        {$array['two'][3]}
        {$object->items[4]->five}
        {${$nasty}}
        {${funcall()}}
        {${$object->method()}}
        {$object->$variable}
        {$object->$variable[1]}
        {${static_class::variable}}
        {${static_class::$variable}}
    "
    ?>"""
    expected = [
        ('QUOTE', '"'),
        ('ENCAPSED_AND_WHITESPACE', "\n        a"),
        ('DOLLAR_OPEN_CURLY_BRACES', "${"), ('STRING_VARNAME', "dollar_curly"), ('RBRACE', '}'),
        ('ENCAPSED_AND_WHITESPACE', "b\n        c"),
        ('CURLY_OPEN', "{"), ('VARIABLE', "$curly_dollar"), ('RBRACE', '}'),
        ('ENCAPSED_AND_WHITESPACE', "d\n        e"),
        ('DOLLAR_OPEN_CURLY_BRACES', "${"), ('VARIABLE', "$dollar_curly_dollar"), ('RBRACE', '}'),
        ('ENCAPSED_AND_WHITESPACE', "f\n        "),
        ('CURLY_OPEN', "{"), ('VARIABLE', "$array"),
        ('LBRACKET', '['), ('LNUMBER', "0"), ('RBRACKET', ']'),
        ('LBRACKET', '['), ('LNUMBER', "1"), ('RBRACKET', ']'),
        ('RBRACE', '}'),
        ('ENCAPSED_AND_WHITESPACE', "\n        "),
        ('CURLY_OPEN', "{"), ('VARIABLE', "$array"),
        ('LBRACKET', '['), ('CONSTANT_ENCAPSED_STRING', "'two'"), ('RBRACKET', ']'),
        ('LBRACKET', '['), ('LNUMBER', "3"), ('RBRACKET', ']'),
        ('RBRACE', '}'),
        ('ENCAPSED_AND_WHITESPACE', "\n        "),
        ('CURLY_OPEN', "{"), ('VARIABLE', "$object"),
        ('OBJECT_OPERATOR', "->"), ('STRING', "items"),
        ('LBRACKET', '['), ('LNUMBER', "4"), ('RBRACKET', ']'),
        ('OBJECT_OPERATOR', "->"), ('STRING', "five"),
        ('RBRACE', '}'),
        ('ENCAPSED_AND_WHITESPACE', "\n        "),
        ('CURLY_OPEN', "{"), ('DOLLAR', '$'), ('LBRACE', '{'),
        ('VARIABLE', "$nasty"), ('RBRACE', '}'), ('RBRACE', '}'),
        ('ENCAPSED_AND_WHITESPACE', "\n        "),
        ('CURLY_OPEN', "{"), ('DOLLAR', "$"), ('LBRACE', "{"), ('STRING', "funcall"),
        ('LPAREN', "("), ('RPAREN', ")"), ('RBRACE', '}'), ('RBRACE', '}'),
        ('ENCAPSED_AND_WHITESPACE', "\n        "),
        ('CURLY_OPEN', "{"), ('DOLLAR', "$"), ('LBRACE', "{"),
        ('VARIABLE', "$object"), ('OBJECT_OPERATOR', "->"), ('STRING', "method"),
        ('LPAREN', "("), ('RPAREN', ")"),
        ('RBRACE', '}'), ('RBRACE', '}'),
        ('ENCAPSED_AND_WHITESPACE', "\n        "),
        ('CURLY_OPEN', "{"),
        ('VARIABLE', "$object"), ('OBJECT_OPERATOR', "->"), ('VARIABLE', "$variable"),
        ('RBRACE', '}'),
        ('ENCAPSED_AND_WHITESPACE', "\n        "),
        ('CURLY_OPEN', "{"),
        ('VARIABLE', "$object"), ('OBJECT_OPERATOR', "->"), ('VARIABLE', "$variable"),
        ('LBRACKET', '['), ('LNUMBER', "1"), ('RBRACKET', ']'),
        ('RBRACE', '}'),
        ('ENCAPSED_AND_WHITESPACE', "\n        "),
        ('CURLY_OPEN', "{"), ('DOLLAR', "$"), ('LBRACE', "{"),
        ('STRING', "static_class"), ('DOUBLE_COLON', "::"), ('STRING', "variable"),
        ('RBRACE', '}'), ('RBRACE', '}'),
        ('ENCAPSED_AND_WHITESPACE', "\n        "),
        ('CURLY_OPEN', "{"), ('DOLLAR', "$"), ('LBRACE', "{"),
        ('STRING', "static_class"), ('DOUBLE_COLON', "::"), ('VARIABLE', "$variable"),
        ('RBRACE', '}'), ('RBRACE', '}'),
        ('ENCAPSED_AND_WHITESPACE', "\n    "),
        ('QUOTE', '"'),
    ]
    eq_tokens(input, expected)

def test_heredoc():
    input = r"""<?
        echo <<<EOT
This is a "$heredoc" with some $embedded->variables
This is not the EOT; this is:
EOT;
    ?>"""
    expected = [
        ('OPEN_TAG', '<?'),
        ('WHITESPACE', '\n        '),
        ('ECHO', 'echo'),
        ('WHITESPACE', ' '),
        ('START_HEREDOC', '<<<EOT\n'),
        ('ENCAPSED_AND_WHITESPACE', 'This'),     # We fudge a bit, producing more
        ('ENCAPSED_AND_WHITESPACE', ' is a "'),  # tokens than necessary.
        ('VARIABLE', '$heredoc'),
        ('ENCAPSED_AND_WHITESPACE', '" with some '),
        ('VARIABLE', '$embedded'),
        ('OBJECT_OPERATOR', '->'),
        ('STRING', 'variables'),
        ('ENCAPSED_AND_WHITESPACE', '\n'),
        ('ENCAPSED_AND_WHITESPACE', 'This'),
        ('ENCAPSED_AND_WHITESPACE', ' is not the EOT; this is:\n'),
        ('END_HEREDOC', 'EOT'),
        ('SEMI', ';'),
        ('WHITESPACE', '\n    '),
        ('CLOSE_TAG', '?>'),
    ]
    eq_tokens(input, expected, ignore=())

def test_heredoc_backslash_newline():
    input = r"""<?
        echo <<<EOT
oh noes!\
EOT;
    ?>"""
    expected = [
        ('OPEN_TAG', '<?'),
        ('WHITESPACE', '\n        '),
        ('ECHO', 'echo'),
        ('WHITESPACE', ' '),
        ('START_HEREDOC', '<<<EOT\n'),
        ('ENCAPSED_AND_WHITESPACE', 'oh'),
        ('ENCAPSED_AND_WHITESPACE', ' noes!'),
        ('ENCAPSED_AND_WHITESPACE', '\\\n'),
        ('END_HEREDOC', 'EOT'),
        ('SEMI', ';'),
        ('WHITESPACE', '\n    '),
        ('CLOSE_TAG', '?>'),
    ]
    eq_tokens(input, expected, ignore=())
    
def test_commented_close_tag():
    input = '<? {\n// ?>\n<?\n} ?>'
    expected = [
        ('OPEN_TAG', '<?'),
        ('WHITESPACE', ' '),
        ('LBRACE', '{'),
        ('WHITESPACE', '\n'),
        ('COMMENT', '// '),
        ('CLOSE_TAG', '?>\n'),  # PHP seems inconsistent regarding
        ('OPEN_TAG', '<?'),     # when \n is included in CLOSE_TAG
        ('WHITESPACE', '\n'),
        ('RBRACE', '}'),
        ('WHITESPACE', ' '),
        ('CLOSE_TAG', '?>'),
    ]
    eq_tokens(input, expected, ignore=())

def test_punctuation():
    input = '<? ([{}]):;,.@ ?>'
    expected = [
        ('LPAREN', '('),
        ('LBRACKET', '['),
        ('LBRACE', '{'),
        ('RBRACE', '}'),
        ('RBRACKET', ']'),
        ('RPAREN', ')'),
        ('COLON', ':'),
        ('SEMI', ';'),
        ('COMMA', ','),
        ('CONCAT', '.'),
        ('AT', '@'),
    ]
    eq_tokens(input, expected)

def test_backticks():
    input = '<? `ls $one`; "`o``ne`"; \'`one`\'; ?>'
    expected = [
        ('BACKTICK', '`'),
        ('ENCAPSED_AND_WHITESPACE', 'ls '),
        ('VARIABLE', '$one'),
        ('BACKTICK', '`'),
        ('SEMI', ';'),
        ('QUOTE', '"'),
        ('ENCAPSED_AND_WHITESPACE', '`o``ne`'),
        ('QUOTE', '"'),
        ('SEMI', ';'),
        ('CONSTANT_ENCAPSED_STRING', "'`one`'"),
        ('SEMI', ';'),
    ]
    eq_tokens(input, expected)

def test_exceptions():
    input = '<? try {} catch {} finally {}'
    expected = [
        ('TRY','try'),
        ('LBRACE','{'),
        ('RBRACE','}'),
        ('CATCH','catch'),
        ('LBRACE','{'),
        ('RBRACE','}'),
        ('FINALLY','finally'),
        ('LBRACE','{'),
        ('RBRACE','}'),
    ]
    eq_tokens(input, expected)

def test_exit_die():
    input = '<? exit(); die;'
    expected = [
        ('EXIT', 'exit'),
        ('LPAREN', '('),
        ('RPAREN', ')'),
        ('SEMI', ';'),
        ('DIE', 'die'),
        ('SEMI', ';'),
    ]
    eq_tokens(input, expected)
