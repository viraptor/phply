from phply.phplex import lexer
import nose.tools

def eq_tokens(input, expected, ignore=('WHITESPACE', 'OPEN_TAG', 'CLOSE_TAG')):
    output = []
    lexer.input(input)
    while True:
        tok = lexer.token()
        if not tok: break
        if tok.type in ignore: continue
        output.append((tok.type, tok.value))
    # print output
    for out, exp in zip(output, expected):
        nose.tools.eq_(out, exp)

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
        'backslash\
escape'
        ""
        "hello"
        "$world"
        "hello $cruel \"world\""
        "end$"
        "newlines
"
        "backslash\
escape"
    ?>"""
    expected = [
        ('CONSTANT_ENCAPSED_STRING', "''"),
        ('CONSTANT_ENCAPSED_STRING', "'hello'"),
        ('CONSTANT_ENCAPSED_STRING', "'what\\'s up'"),
        ('CONSTANT_ENCAPSED_STRING', "'newlines\n'"),
        ('CONSTANT_ENCAPSED_STRING', "'backslash\\\nescape'"),
        ('QUOTE', '"'), ('QUOTE', '"'),
        ('QUOTE', '"'), ('ENCAPSED_AND_WHITESPACE', 'hello'), ('QUOTE', '"'),
        ('QUOTE', '"'), ('VARIABLE', '$world'), ('QUOTE', '"'),
        ('QUOTE', '"'), ('ENCAPSED_AND_WHITESPACE', 'hello '),
        ('VARIABLE', '$cruel'), ('ENCAPSED_AND_WHITESPACE', ' \\"world\\"'), ('QUOTE', '"'),
        ('QUOTE', '"'), ('ENCAPSED_AND_WHITESPACE', 'end$'), ('QUOTE', '"'),
        ('QUOTE', '"'), ('ENCAPSED_AND_WHITESPACE', 'newlines\n'), ('QUOTE', '"'),
        ('QUOTE', '"'), ('ENCAPSED_AND_WHITESPACE', 'backslash\\\nescape'), ('QUOTE', '"'),
    ]
    eq_tokens(input, expected)

def test_punct():
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
