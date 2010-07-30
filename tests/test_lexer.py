from phply.phplex import lexer
import nose.tools

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
    output = []
    lexer.input(input)
    while True:
        tok = lexer.token()
        if not tok: break
        if tok.type in ('WHITESPACE', 'OPEN_TAG', 'CLOSE_TAG'): continue
        output.append((tok.type, tok.value))
    for out, exp in zip(output, expected):
        nose.tools.eq_(out, exp)
