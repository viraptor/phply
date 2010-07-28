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

precedence = (
    ('left', 'INCLUDE', 'INCLUDE_ONCE', 'EVAL', 'REQUIRE', 'REQUIRE_ONCE'),
    ('left', 'COMMA'),
    ('left', 'LOGICAL_OR'),
    ('left', 'LOGICAL_XOR'),
    ('left', 'LOGICAL_AND'),
    ('right', 'PRINT'),
    ('left', 'EQUALS', 'PLUS_EQUAL', 'MINUS_EQUAL', 'MUL_EQUAL', 'DIV_EQUAL', 'CONCAT_EQUAL', 'MOD_EQUAL', 'AND_EQUAL', 'OR_EQUAL', 'XOR_EQUAL', 'SL_EQUAL', 'SR_EQUAL'),
    ('left', 'QUESTION', 'COLON'),
    ('left', 'BOOLEAN_OR'),
    ('left', 'BOOLEAN_AND'),
    ('left', 'OR'),
    ('left', 'XOR'),
    ('left', 'AND'),
    ('nonassoc', 'IS_EQUAL', 'IS_NOT_EQUAL', 'IS_IDENTICAL', 'IS_NOT_IDENTICAL'),
    ('nonassoc', 'IS_SMALLER', 'IS_SMALLER_OR_EQUAL', 'IS_GREATER', 'IS_GREATER_OR_EQUAL'),
    ('left', 'SL', 'SR'),
    ('left', 'PLUS', 'MINUS', 'CONCAT'),
    ('left', 'MUL', 'DIV', 'MOD'),
    ('right', 'BOOLEAN_NOT'),
    ('nonassoc', 'INSTANCEOF'),
    ('right', 'NOT', 'INC', 'DEC', 'INT_CAST', 'DOUBLE_CAST', 'STRING_CAST', 'ARRAY_CAST', 'OBJECT_CAST', 'BOOL_CAST', 'UNSET_CAST', 'AT'),
    ('right', 'LBRACKET'),
    ('nonassoc', 'NEW', 'CLONE'),
    # ('left', 'ELSEIF'),
    # ('left', 'ELSE'),
    ('left', 'ENDIF'),
    ('right', 'STATIC', 'ABSTRACT', 'FINAL', 'PRIVATE', 'PROTECTED', 'PUBLIC'),
)

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
                     | function_declaration_statement
                     | class_declaration_statement
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
                       | function_declaration_statement
                       | class_declaration_statement
                       | HALT_COMPILER LPAREN RPAREN SEMI'''
    assert len(p) == 2, "__HALT_COMPILER() can only be used from the outermost scope"
    p[0] = p[1]

def p_statement_block(p):
    'statement : LBRACE inner_statement_list RBRACE'
    p[0] = ast.Block(p[2])

def p_statement_if(p):
    '''statement : IF LPAREN expr RPAREN statement elseif_list else_single
                 | IF LPAREN expr RPAREN COLON inner_statement_list new_elseif_list new_else_single ENDIF SEMI'''
    if len(p) == 8:
        p[0] = ast.If(p[3], p[5], p[6], p[7])
    else:
        p[0] = ast.If(p[3], ast.Block(p[6]), p[7], p[8])

# todo: while
# todo: do/while
# todo: for
# todo: switch

def p_statement_break(p):
    '''statement : BREAK SEMI
                 | BREAK expr SEMI'''
    if len(p) == 3:
        p[0] = ast.Break(None)
    else:
        p[0] = ast.Break(p[2])

def p_statement_continue(p):
    '''statement : CONTINUE SEMI
                 | CONTINUE expr SEMI'''
    if len(p) == 3:
        p[0] = ast.Continue(None)
    else:
        p[0] = ast.Continue(p[2])

def p_statement_return(p):
    '''statement : RETURN SEMI
                 | RETURN expr SEMI'''
    if len(p) == 3:
        p[0] = ast.Return(None)
    else:
        p[0] = ast.Return(p[2])

def p_statement_global(p):
    'statement : GLOBAL global_var_list SEMI'
    p[0] = ast.Global(p[2])

def p_statement_static(p):
    'statement : STATIC static_var_list SEMI'
    p[0] = ast.Static(p[2])

def p_statement_open_tag_with_echo(p):
    'statement : OPEN_TAG_WITH_ECHO expr CLOSE_TAG'
    p[0] = ast.Echo([p[2]])

def p_statement_echo(p):
    'statement : ECHO echo_expr_list SEMI'
    p[0] = ast.Echo(p[2])

def p_statement_inline_html(p):
    'statement : INLINE_HTML'
    p[0] = ast.InlineHTML(p[1])

def p_statement_expr(p):
    'statement : expr SEMI'
    p[0] = p[1]

def p_statement_unset(p):
    'statement : UNSET LPAREN unset_variables RPAREN SEMI'
    p[0] = ast.Unset(p[3])

# todo: foreach

def p_statement_empty(p):
    'statement : SEMI'
    pass

# todo: try/catch
# todo: throw

def p_elseif_list(p):
    '''elseif_list : empty
                   | elseif_list ELSEIF LPAREN expr RPAREN statement'''
    if len(p) == 2:
        p[0] = []
    else:
        p[0] = p[1] + [ast.ElseIf(p[4], p[6])]

def p_else_single(p):
    '''else_single : empty
                   | ELSE statement'''
    if len(p) == 3:
        p[0] = ast.Else(p[2])

def p_new_elseif_list(p):
    '''new_elseif_list : empty
                       | new_elseif_list ELSEIF LPAREN expr RPAREN COLON inner_statement_list'''
    if len(p) == 2:
        p[0] = []
    else:
        p[0] = p[1] + [ast.ElseIf(p[4], ast.Block(p[7]))]

def p_new_else_single(p):
    '''new_else_single : empty
                       | ELSE COLON inner_statement_list'''
    if len(p) == 4:
        p[0] = ast.Else(ast.Block(p[3]))

def p_global_var_list(p):
    '''global_var_list : global_var_list COMMA global_var
                       | global_var'''
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = [p[1]]

def p_global_var(p):
    'global_var : VARIABLE'
    p[0] = ast.Variable(p[1])

def p_static_var_list(p):
    '''static_var_list : static_var_list COMMA static_var
                       | static_var'''
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = [p[1]]

def p_static_var(p):
    '''static_var : VARIABLE EQUALS static_scalar
                  | VARIABLE'''
    if len(p) == 4:
        p[0] = ast.StaticVariable(p[1], p[3])
    else:
        p[0] = ast.StaticVariable(p[1], None)

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

def p_function_declaration_statement(p):
    'function_declaration_statement : FUNCTION is_reference STRING LPAREN parameter_list RPAREN LBRACE inner_statement_list RBRACE'
    p[0] = ast.Function(p[3], p[5], p[8], p[2])

def p_class_declaration_statement(p):
    'class_declaration_statement : CLASS'
    # todo

def p_is_reference(p):
    '''is_reference : AND
                    | empty'''
    p[0] = p[1] is not None

def p_parameter_list(p):
    '''parameter_list : parameter_list COMMA parameter
                      | parameter'''
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = [p[1]]

def p_parameter_list_empty(p):
    'parameter_list : empty'
    p[0] = []

def p_parameter(p):
    '''parameter : VARIABLE
                 | AND VARIABLE
                 | VARIABLE EQUALS static_scalar
                 | AND VARIABLE EQUALS static_scalar'''
    if len(p) == 2:
        p[0] = ast.FormalParameter(p[1], None, False)
    elif len(p) == 3:
        p[0] = ast.FormalParameter(p[2], None, True)
    elif len(p) == 4:
        p[0] = ast.FormalParameter(p[1], p[3], False)
    else:
        p[0] = ast.FormalParameter(p[2], p[4], True)

def p_expr_variable(p):
    'expr : variable'
    p[0] = p[1]

def p_expr_assign(p):
    '''expr : variable EQUALS expr
            | variable EQUALS AND expr'''
    if len(p) == 5:
        p[0] = ast.Assignment(p[1], p[4], True)
    else:
        p[0] = ast.Assignment(p[1], p[3], False)

def p_expr_list_assign(p):
    'expr : LIST LPAREN assignment_list RPAREN EQUALS expr'
    p[0] = ast.ListAssignment(p[3], p[6])

def p_assignment_list(p):
    '''assignment_list : assignment_list COMMA assignment_list_element
                       | assignment_list_element'''
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = [p[1]]

def p_assignment_list_element(p):
    '''assignment_list_element : variable
                               | empty
                               | LIST LPAREN assignment_list RPAREN'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = p[3]

def p_variable(p):
    'variable : VARIABLE'
    p[0] = ast.Variable(p[1])

def p_variable_array_offset(p):
    'variable : variable LBRACKET dim_offset RBRACKET'
    p[0] = ast.ArrayOffset(p[1], p[3])

def p_variable_string_offset(p):
    'variable : variable LBRACE expr RBRACE'
    p[0] = ast.StringOffset(p[1], p[3])

def p_dim_offset(p):
    '''dim_offset : expr
                  | empty'''
    p[0] = p[1]

def p_expr_scalar(p):
    'expr : scalar'
    p[0] = p[1]

def p_expr_array(p):
    'expr : ARRAY LPAREN array_pair_list RPAREN'
    p[0] = ast.Array(p[3])

def p_array_pair_list(p):
    '''array_pair_list : empty
                       | non_empty_array_pair_list possible_comma'''
    if len(p) == 2:
        p[0] = []
    else:
        p[0] = p[1]

def p_non_empty_array_pair_list_item(p):
    '''non_empty_array_pair_list : non_empty_array_pair_list COMMA AND variable
                                 | non_empty_array_pair_list COMMA expr
                                 | AND variable
                                 | expr'''
    if len(p) == 5:
        p[0] = p[1] + [ast.ArrayElement(None, p[4], True)]
    elif len(p) == 4:
        p[0] = p[1] + [ast.ArrayElement(None, p[3], False)]
    elif len(p) == 3:
        p[0] = [ast.ArrayElement(None, p[2], True)]
    else:
        p[0] = [ast.ArrayElement(None, p[1], False)]

def p_non_empty_array_pair_list_pair(p):
    '''non_empty_array_pair_list : non_empty_array_pair_list COMMA expr DOUBLE_ARROW AND variable
                                 | non_empty_array_pair_list COMMA expr DOUBLE_ARROW expr
                                 | expr DOUBLE_ARROW AND variable
                                 | expr DOUBLE_ARROW expr'''
    if len(p) == 7:
        p[0] = p[1] + [ast.ArrayElement(p[3], p[6], True)]
    elif len(p) == 6:
        p[0] = p[1] + [ast.ArrayElement(p[3], p[5], False)]
    elif len(p) == 5:
        p[0] = [ast.ArrayElement(p[1], p[4], True)]
    else:
        p[0] = [ast.ArrayElement(p[1], p[3], False)]

def p_possible_comma(p):
    '''possible_comma : empty
                      | COMMA'''
    pass

def p_expr_function_call(p):
    'expr : STRING LPAREN function_call_parameter_list RPAREN'
    p[0] = ast.FunctionCall(p[1], p[3])

def p_function_call_parameter_list(p):
    '''function_call_parameter_list : function_call_parameter_list COMMA function_call_parameter
                                    | function_call_parameter'''
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = [p[1]]

def p_function_call_parameter_list_empty(p):
    'function_call_parameter_list : empty'
    p[0] = []

def p_function_call_parameter(p):
    '''function_call_parameter : expr
                               | AND variable'''
    if len(p) == 2:
        p[0] = ast.Parameter(p[1], False)
    else:
        p[0] = ast.Parameter(p[2], True)

def p_expr_binary_op(p):
    '''expr : expr BOOLEAN_AND expr
            | expr BOOLEAN_OR expr
            | expr LOGICAL_AND expr
            | expr LOGICAL_OR expr
            | expr LOGICAL_XOR expr
            | expr AND expr
            | expr OR expr
            | expr XOR expr
            | expr CONCAT expr
            | expr PLUS expr
            | expr MINUS expr
            | expr MUL expr
            | expr DIV expr
            | expr SL expr
            | expr SR expr
            | expr MOD expr
            | expr IS_IDENTICAL expr
            | expr IS_NOT_IDENTICAL expr
            | expr IS_EQUAL expr
            | expr IS_NOT_EQUAL expr
            | expr IS_SMALLER expr
            | expr IS_SMALLER_OR_EQUAL expr
            | expr IS_GREATER expr
            | expr IS_GREATER_OR_EQUAL expr'''
    p[0] = ast.BinaryOp(p[2], p[1], p[3])

def p_expr_unary_op(p):
    '''expr : PLUS expr
            | MINUS expr
            | NOT expr
            | BOOLEAN_NOT expr'''
    p[0] = ast.UnaryOp(p[1], p[2])

def p_expr_group(p):
    'expr : LPAREN expr RPAREN'
    p[0] = p[2]

def p_scalar(p):
    '''scalar : common_scalar
              | namespace_name
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

def p_static_scalar(p):
    '''static_scalar : common_scalar
                     | namespace_name
                     | QUOTE ENCAPSED_AND_WHITESPACE QUOTE'''
    if len(p) == 4:
        p[0] = p[2]
    else:
        p[0] = p[1]

def p_namespace_name(p):
    'namespace_name : STRING'
    p[0] = ast.Constant(p[1])

def p_encaps_list(p):
    '''encaps_list : encaps_list encaps_var
                   | encaps_list ENCAPSED_AND_WHITESPACE
                   | empty'''
    if len(p) == 3:
        if p[1] == '':
            p[0] = p[2]
        else:
            p[0] = ast.BinaryOp('.', p[1], p[2])
    else:
        p[0] = ''

def p_encaps_var(p):
    'encaps_var : VARIABLE'
    p[0] = ast.Variable(p[1])

def p_empty(t):
    'empty : '
    pass

# Error rule for syntax errors
def p_error(t):
    if t and t.type in ('WHITESPACE', 'OPEN_TAG', 'CLOSE_TAG', 'COMMENT', 'DOC_COMMENT'):
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
