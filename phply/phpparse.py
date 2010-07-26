# -----------------------------------------------------------------------------
# phpparse.py
#
# A parser for PHP.
# -----------------------------------------------------------------------------

import sys
import phplex
import phpast as ast
import ply.yacc as yacc

# Get the token map
tokens = phplex.tokens

def p_start(p):
    'start : top_statement_list'
    p[0] = p[1]

def p_top_statement_list(p):
    '''top_statement_list : top_statement_list top_statement
                          | empty'''
    if len(p) == 3:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = []

def p_top_statement(p):
    '''top_statement : statement
                     | HALT_COMPILER LPAREN RPAREN SEMI'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        # ???
        pass

def p_inner_statement_list(p):
    '''inner_statement_list : inner_statement_list inner_statement
                            | empty'''
    if len(p) == 3:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = []

def p_inner_statement(p):
    '''inner_statement : statement
                       | HALT_COMPILER LPAREN RPAREN SEMI'''
    assert len(p) == 2, "__HALT_COMPILER() can only be used from the outermost scope"
    p[0] = p[1]

def p_statement_block(p):
    'statement : LBRACE inner_statement_list RBRACE'
    p[0] = ast.Block([p[2]])

# todo: if/elseif/else
# todo: while
# todo: do/while
# todo: for
# todo: switch

def p_statement_break(p):
    '''statement : BREAK SEMI
                 | BREAK expr SEMI'''
    if len(p) == 3:
        p[0] = ast.Break([None])
    else:
        p[0] = ast.Break([p[2]])

def p_statement_continue(p):
    '''statement : CONTINUE SEMI
                 | CONTINUE expr SEMI'''
    if len(p) == 3:
        p[0] = ast.Continue([None])
    else:
        p[0] = ast.Continue([p[2]])

def p_statement_return(p):
    '''statement : RETURN SEMI
                 | RETURN expr SEMI'''
    if len(p) == 3:
        p[0] = ast.Return([None])
    else:
        p[0] = ast.Return([p[2]])

def p_statement_global(p):
    'statement : GLOBAL global_var_list SEMI'
    p[0] = ast.Global([p[2]])

# todo: static

def p_statement_open_tag_with_echo(p):
    'statement : OPEN_TAG_WITH_ECHO expr CLOSE_TAG'
    p[0] = ast.Echo([[p[2]]])

def p_statement_echo(p):
    'statement : ECHO echo_expr_list SEMI'
    p[0] = ast.Echo([p[2]])

def p_statement_inline_html(p):
    'statement : INLINE_HTML'
    p[0] = ast.InlineHTML([p[1]])

def p_statement_expr(p):
    'statement : expr SEMI'
    p[0] = p[1]

def p_statement_unset(p):
    'statement : UNSET LPAREN unset_variables RPAREN SEMI'
    p[0] = ast.Unset([p[3]])

# todo: foreach

def p_statement_empty(p):
    'statement : SEMI'
    p[0] = ast.EmptyNode([])

# todo: try/catch
# todo: throw

def p_global_var_list(p):
    '''global_var_list : global_var_list COMMA global_var
                       | global_var'''
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = [p[1]]

def p_global_var(p):
    'global_var : VARIABLE'
    p[0] = ast.Variable([p[1]])

def p_echo_expr_list(p):
    '''echo_expr_list : echo_expr_list COMMA expr
                      | expr'''
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = [p[1]]

def p_unset_variables(p):
    '''unset_variables : unset_variables COMMA unset_variable
                       | unset_variable'''
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = [p[1]]

def p_unset_variable(p):
    'unset_variable : variable'
    p[0] = p[1]

def p_expr_variable(p):
    'expr : variable'
    p[0] = p[1]

def p_expr_assign(p):
    'expr : variable EQUALS expr'
    # todo: ref
    p[0] = ast.Assignment([p[1], p[3]])

def p_expr_list_assign(p):
    'expr : LIST LPAREN assignment_list RPAREN EQUALS expr'
    p[0] = ast.ListAssignment([p[3], p[6]])

def p_assignment_list(p):
    '''assignment_list : assignment_list COMMA assignment_list_element
                       | assignment_list_element'''
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = [p[1]]

def p_assignment_list_element(p):
    '''assignment_list_element : variable
                               | LIST LPAREN assignment_list RPAREN'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = p[3]

def p_assignment_list_element_empty(p):
    'assignment_list_element : empty'
    p[0] = ast.EmptyNode([])

def p_variable(p):
    'variable : VARIABLE'
    p[0] = ast.Variable([p[1]])

def p_expr_scalar(p):
    'expr : scalar'
    p[0] = p[1]

def p_expr_binary_op(p):
    '''expr : expr PLUS expr
            | expr MINUS expr
            | expr MUL expr
            | expr DIV expr'''
    p[0] = ast.BinaryOp([p[2], p[1], p[3]])

def p_expr_group(p):
    'expr : LPAREN expr RPAREN'
    p[0] = p[2]

def p_scalar(p):
    '''scalar : common_scalar
              | QUOTE encaps_list QUOTE'''
    if len(p) == 4:
        p[0] = p[2]
    else:
        p[0] = p[1]

def p_common_scalar_lnumber(p):
    'common_scalar : LNUMBER'
    if p[1].startswith('0x'):
        p[0] = int(p[1], 16)
    elif p[1].startswith('0'):
        p[0] = int(p[1], 8)
    else:
        p[0] = int(p[1])

def p_common_scalar_dnumber(p):
    'common_scalar : DNUMBER'
    p[0] = float(p[1])

def p_common_scalar_string(p):
    'common_scalar : CONSTANT_ENCAPSED_STRING'
    p[0] = p[1][1:-1]

def p_encaps_list(p):
    '''encaps_list : encaps_list encaps_var
                   | encaps_list ENCAPSED_AND_WHITESPACE
                   | encaps_var
                   | ENCAPSED_AND_WHITESPACE encaps_var'''
    if len(p) == 3:
        p[0] = ast.BinaryOp(['.', p[1], p[2]])
    else:
        p[0] = p[1]

def p_encaps_list_empty(p):
    'encaps_list : empty'
    p[0] = ''

def p_encaps_var(p):
    'encaps_var : VARIABLE'
    p[0] = ast.Variable([p[1]])

def p_empty(t):
    'empty : '
    pass

# Error rule for syntax errors
def p_error(t):
    if t and t.type in ('WHITESPACE', 'OPEN_TAG', 'CLOSE_TAG'):
        yacc.errok()
    else:
        print 'Parse error at', t

# Build the grammar
parser = yacc.yacc(debug=1)
# parser = yacc.yacc(method='LALR')

# import profile
# profile.run("yacc.yacc(method='LALR')")

if __name__ == '__main__':
    import readline
    import pprint
    while True:
       try:
           s = raw_input('php> ')
       except EOFError:
           break
       if not s: continue
       # result = parser.parse('<?php ' + s + '; ?>')
       # result = parser.parse('<?= ' + s + ' ?>')
       result = parser.parse(s)
       # print result
       if result:
           for item in result:
               if hasattr(item, 'generic'):
                   item = item.generic()
               pprint.pprint(item)
