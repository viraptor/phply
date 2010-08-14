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
    p[0] = ast.Block(p[2], lineno=p.lineno(1))

def p_statement_if(p):
    '''statement : IF LPAREN expr RPAREN statement elseif_list else_single
                 | IF LPAREN expr RPAREN COLON inner_statement_list new_elseif_list new_else_single ENDIF semi'''
    if len(p) == 8:
        p[0] = ast.If(p[3], p[5], p[6], p[7], lineno=p.lineno(1))
    else:
        p[0] = ast.If(p[3], ast.Block(p[6], lineno=p.lineno(5)),
                      p[7], p[8], lineno=p.lineno(1))

def p_statement_while(p):
    'statement : WHILE LPAREN expr RPAREN while_statement'
    p[0] = ast.While(p[3], p[5], lineno=p.lineno(1))

def p_statement_do_while(p):
    'statement : DO statement WHILE LPAREN expr RPAREN semi'
    p[0] = ast.DoWhile(p[2], p[5], lineno=p.lineno(1))

def p_statement_for(p):
    'statement : FOR LPAREN for_expr SEMI for_expr SEMI for_expr RPAREN for_statement'
    p[0] = ast.For(p[3], p[5], p[7], p[9], lineno=p.lineno(1))

def p_statement_foreach(p):
    'statement : FOREACH LPAREN expr AS foreach_variable foreach_optional_arg RPAREN foreach_statement'
    if p[6] is None:
        p[0] = ast.Foreach(p[3], None, p[5], p[8], lineno=p.lineno(1))
    else:
        p[0] = ast.Foreach(p[3], p[5], p[6], p[8], lineno=p.lineno(1))

def p_statement_switch(p):
    'statement : SWITCH LPAREN expr RPAREN switch_case_list'
    p[0] = ast.Switch(p[3], p[5], lineno=p.lineno(1))

def p_statement_break(p):
    '''statement : BREAK semi
                 | BREAK expr semi'''
    if len(p) == 3:
        p[0] = ast.Break(None, lineno=p.lineno(1))
    else:
        p[0] = ast.Break(p[2], lineno=p.lineno(1))

def p_statement_continue(p):
    '''statement : CONTINUE semi
                 | CONTINUE expr semi'''
    if len(p) == 3:
        p[0] = ast.Continue(None, lineno=p.lineno(1))
    else:
        p[0] = ast.Continue(p[2], lineno=p.lineno(1))

def p_statement_return(p):
    '''statement : RETURN semi
                 | RETURN expr semi'''
    if len(p) == 3:
        p[0] = ast.Return(None, lineno=p.lineno(1))
    else:
        p[0] = ast.Return(p[2], lineno=p.lineno(1))

def p_statement_global(p):
    'statement : GLOBAL global_var_list semi'
    p[0] = ast.Global(p[2], lineno=p.lineno(1))

def p_statement_static(p):
    'statement : STATIC static_var_list semi'
    p[0] = ast.Static(p[2], lineno=p.lineno(1))

def p_statement_open_tag_with_echo(p):
    'statement : OPEN_TAG_WITH_ECHO expr CLOSE_TAG'
    p[0] = ast.Echo([p[2]], lineno=p.lineno(1))

def p_statement_echo(p):
    'statement : ECHO echo_expr_list semi'
    p[0] = ast.Echo(p[2], lineno=p.lineno(1))

def p_statement_inline_html(p):
    'statement : INLINE_HTML'
    p[0] = ast.InlineHTML(p[1], lineno=p.lineno(1))

def p_statement_expr(p):
    'statement : expr semi'
    p[0] = p[1]

def p_statement_unset(p):
    'statement : UNSET LPAREN unset_variables RPAREN semi'
    p[0] = ast.Unset(p[3], lineno=p.lineno(1))

def p_statement_empty(p):
    'statement : SEMI'
    pass

def p_statement_try(p):
    'statement : TRY LBRACE inner_statement_list RBRACE CATCH LPAREN fully_qualified_class_name VARIABLE RPAREN LBRACE inner_statement_list RBRACE additional_catches'
    p[0] = ast.Try(p[3], [ast.Catch(p[7], ast.Variable(p[8], lineno=p.lineno(8)),
                                    p[11], lineno=p.lineno(5))] + p[13],
                   lineno=p.lineno(1))

def p_additional_catches(p):
    '''additional_catches : additional_catches CATCH LPAREN fully_qualified_class_name VARIABLE RPAREN LBRACE inner_statement_list RBRACE
                          | empty'''
    if len(p) == 10:
        p[0] = p[1] + [ast.Catch(p[4], ast.Variable(p[5], lineno=p.lineno(5)),
                                 p[8], lineno=p.lineno(2))]
    else:
        p[0] = []

def p_statement_throw(p):
    'statement : THROW expr semi'
    p[0] = ast.Throw(p[2], lineno=p.lineno(1))

# todo: declare

def p_elseif_list(p):
    '''elseif_list : empty
                   | elseif_list ELSEIF LPAREN expr RPAREN statement'''
    if len(p) == 2:
        p[0] = []
    else:
        p[0] = p[1] + [ast.ElseIf(p[4], p[6], lineno=p.lineno(2))]

def p_else_single(p):
    '''else_single : empty
                   | ELSE statement'''
    if len(p) == 3:
        p[0] = ast.Else(p[2], lineno=p.lineno(1))

def p_new_elseif_list(p):
    '''new_elseif_list : empty
                       | new_elseif_list ELSEIF LPAREN expr RPAREN COLON inner_statement_list'''
    if len(p) == 2:
        p[0] = []
    else:
        p[0] = p[1] + [ast.ElseIf(p[4], ast.Block(p[7], lineo=p.lineno(6)),
                                  lineno=p.lineno(2))]

def p_new_else_single(p):
    '''new_else_single : empty
                       | ELSE COLON inner_statement_list'''
    if len(p) == 4:
        p[0] = ast.Else(ast.Block(p[3], lineno=p.lineno(2)),
                        lineno=p.lineno(1))

def p_while_statement(p):
    '''while_statement : statement
                       | COLON inner_statement_list ENDWHILE semi'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = ast.Block(p[2], lineno=p.lineno(1))

def p_for_expr(p):
    '''for_expr : empty
                | non_empty_for_expr'''
    p[0] = p[1]

def p_non_empty_for_expr(p):
    '''non_empty_for_expr : non_empty_for_expr COMMA expr
                          | expr'''
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = [p[1]]

def p_for_statement(p):
    '''for_statement : statement
                     | COLON inner_statement_list ENDFOR semi'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = ast.Block(p[2], lineno=p.lineno(1))

def p_foreach_variable(p):
    '''foreach_variable : VARIABLE
                        | AND VARIABLE'''
    if len(p) == 2:
        p[0] = ast.ForeachVariable(p[1], False, lineno=p.lineno(1))
    else:
        p[0] = ast.ForeachVariable(p[2], True, lineno=p.lineno(1))

def p_foreach_optional_arg(p):
    '''foreach_optional_arg : empty
                            | DOUBLE_ARROW foreach_variable'''
    if len(p) == 3:
        p[0] = p[2]

def p_foreach_statement(p):
    '''foreach_statement : statement
                         | COLON inner_statement_list ENDFOREACH semi'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = ast.Block(p[2], lineno=p.lineno(1))

def p_switch_case_list(p):
    '''switch_case_list : LBRACE case_list RBRACE
                        | LBRACE SEMI case_list RBRACE'''
    if len(p) == 4:
        p[0] = p[2]
    else:
        p[0] = p[3]

def p_switch_case_list_colon(p):
    '''switch_case_list : COLON case_list ENDSWITCH semi
                        | COLON SEMI case_list ENDSWITCH semi'''
    if len(p) == 5:
        p[0] = p[2]
    else:
        p[0] = p[3]

def p_case_list(p):
    '''case_list : empty
                 | case_list CASE expr case_separator inner_statement_list
                 | case_list DEFAULT case_separator inner_statement_list'''
    if len(p) == 6:
        p[0] = p[1] + [ast.Case(p[3], p[5], lineno=p.lineno(2))]
    elif len(p) == 5:
        p[0] = p[1] + [ast.Default(p[4], lineno=p.lineno(2))]
    else:
        p[0] = []

def p_case_separator(p):
    '''case_separator : COLON
                      | SEMI'''
    pass

def p_global_var_list(p):
    '''global_var_list : global_var_list COMMA global_var
                       | global_var'''
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = [p[1]]

def p_global_var(p):
    '''global_var : VARIABLE
                  | DOLLAR variable
                  | DOLLAR LBRACE expr RBRACE'''
    if len(p) == 2:
        p[0] = ast.Variable(p[1], lineno=p.lineno(1))
    elif len(p) == 3:
        p[0] = ast.Variable(p[2], lineno=p.lineno(1))
    else:
        p[0] = ast.Variable(p[3], lineno=p.lineno(1))

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
        p[0] = ast.StaticVariable(p[1], p[3], lineno=p.lineno(1))
    else:
        p[0] = ast.StaticVariable(p[1], None, lineno=p.lineno(1))

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
    p[0] = ast.Function(p[3], p[5], p[8], p[2], lineno=p.lineno(1))

def p_class_declaration_statement(p):
    '''class_declaration_statement : class_entry_type STRING extends_from implements_list LBRACE class_statement_list RBRACE
                                   | INTERFACE STRING interface_extends_list LBRACE class_statement_list RBRACE'''
    if len(p) == 8:
        p[0] = ast.Class(p[2], p[1], p[3], p[4], p[6], lineno=p.lineno(2))
    else:
        p[0] = ast.Interface(p[2], p[3], p[5], lineno=p.lineno(1))

def p_class_entry_type(p):
    '''class_entry_type : CLASS
                        | ABSTRACT CLASS
                        | FINAL CLASS'''
    if len(p) == 3:
        p[0] = p[1].lower()

def p_extends_from(p):
    '''extends_from : empty
                    | EXTENDS fully_qualified_class_name'''
    if len(p) == 3:
        p[0] = p[2]

def p_fully_qualified_class_name(p):
    'fully_qualified_class_name : namespace_name'
    p[0] = p[1]

def p_implements_list(p):
    '''implements_list : IMPLEMENTS interface_list
                       | empty'''
    if len(p) == 3:
        p[0] = p[2]
    else:
        p[0] = []

def p_class_statement_list(p):
    '''class_statement_list : class_statement_list class_statement
                            | empty'''

    if len(p) == 3:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = []

def p_class_statement(p):
    '''class_statement : method_modifiers FUNCTION is_reference STRING LPAREN parameter_list RPAREN method_body
                       | variable_modifiers class_variable_declaration SEMI
                       | class_constant_declaration SEMI'''
    if len(p) == 9:
        p[0] = ast.Method(p[4], p[1], p[6], p[8], p[3], lineno=p.lineno(2))
    elif len(p) == 4:
        p[0] = ast.ClassVariables(p[1], p[2], lineno=p.lineno(3))
    else:
        p[0] = ast.ClassConstants(p[1], lineno=p.lineno(2))

def p_class_variable_declaration_initial(p):
    '''class_variable_declaration : class_variable_declaration COMMA VARIABLE EQUALS static_scalar
                                  | VARIABLE EQUALS static_scalar'''
    if len(p) == 6:
        p[0] = p[1] + [ast.ClassVariable(p[3], p[5], lineno=p.lineno(2))]
    else:
        p[0] = [ast.ClassVariable(p[1], p[3], lineno=p.lineno(1))]

def p_class_variable_declaration_no_initial(p):
    '''class_variable_declaration : class_variable_declaration COMMA VARIABLE
                                  | VARIABLE'''
    if len(p) == 4:
        p[0] = p[1] + [ast.ClassVariable(p[3], None, lineno=p.lineno(2))]
    else:
        p[0] = [ast.ClassVariable(p[1], None, lineno=p.lineno(1))]

def p_class_constant_declaration(p):
    '''class_constant_declaration : class_constant_declaration COMMA STRING EQUALS static_scalar
                                  | CONST STRING EQUALS static_scalar'''
    if len(p) == 6:
        p[0] = p[1] + [ast.ClassConstant(p[3], p[5], lineno=p.lineno(2))]
    else:
        p[0] = [ast.ClassConstant(p[2], p[4], lineno=p.lineno(1))]

def p_interface_list(p):
    '''interface_list : interface_list COMMA fully_qualified_class_name
                      | fully_qualified_class_name'''
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = [p[1]]

def p_interface_extends_list(p):
    '''interface_extends_list : EXTENDS interface_list
                              | empty'''
    if len(p) == 3:
        p[0] = p[2]

def p_variable_modifiers_non_empty(p):
    'variable_modifiers : non_empty_member_modifiers'
    p[0] = p[1]

def p_variable_modifiers_var(p):
    'variable_modifiers : VAR'
    p[0] = []

def p_method_modifiers_non_empty(p):
    'method_modifiers : non_empty_member_modifiers'
    p[0] = p[1]

def p_method_modifiers_empty(p):
    'method_modifiers : empty'
    p[0] = []

def p_method_body(p):
    '''method_body : LBRACE inner_statement_list RBRACE
                   | SEMI'''
    if len(p) == 4:
        p[0] = p[2]
    else:
        p[0] = []

def p_non_empty_member_modifiers(p):
    '''non_empty_member_modifiers : non_empty_member_modifiers member_modifier
                                  | member_modifier'''
    if len(p) == 3:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = [p[1]]

def p_member_modifier(p):
    '''member_modifier : PUBLIC
                       | PROTECTED
                       | PRIVATE
                       | STATIC
                       | ABSTRACT
                       | FINAL'''
    p[0] = p[1].lower()

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
        p[0] = ast.FormalParameter(p[1], None, False, lineno=p.lineno(1))
    elif len(p) == 3:
        p[0] = ast.FormalParameter(p[2], None, True, lineno=p.lineno(1))
    elif len(p) == 4:
        p[0] = ast.FormalParameter(p[1], p[3], False, lineno=p.lineno(1))
    else:
        p[0] = ast.FormalParameter(p[2], p[4], True, lineno=p.lineno(1))

def p_expr_variable(p):
    'expr : variable'
    p[0] = p[1]

def p_expr_assign(p):
    '''expr : variable EQUALS expr
            | variable EQUALS AND expr'''
    if len(p) == 5:
        p[0] = ast.Assignment(p[1], p[4], True, lineno=p.lineno(2))
    else:
        p[0] = ast.Assignment(p[1], p[3], False, lineno=p.lineno(2))

def p_expr_new(p):
    'expr : NEW class_name_reference ctor_arguments'
    p[0] = ast.New(p[2], p[3], lineno=p.lineno(1))

def p_class_name_reference(p):
    '''class_name_reference : class_name
                            | dynamic_class_name_reference'''
    p[0] = p[1]

def p_class_name(p):
    'class_name : namespace_name'
    p[0] = p[1]                  

def p_dynamic_class_name_reference(p):
    '''dynamic_class_name_reference : base_variable OBJECT_OPERATOR object_property dynamic_class_name_variable_properties
                                    | base_variable'''
    # todo
    pass

def p_dynamic_class_name_variable_properties(p):
    '''dynamic_class_name_variable_properties : dynamic_class_name_variable_properties dynamic_class_name_variable_property
                                              | empty'''
    # todo
    pass

def p_dynamic_class_name_variable_property(p):
    'dynamic_class_name_variable_property : OBJECT_OPERATOR object_property'
    # todo
    pass

def p_ctor_arguments(p):
    '''ctor_arguments : LPAREN function_call_parameter_list RPAREN
                      | empty'''
    if len(p) == 4:
        p[0] = p[2]
    else:
        p[0] = []

def p_expr_clone(p):
    'expr : CLONE expr'
    p[0] = ast.Clone(p[2], lineno=p.lineno(1))

def p_expr_list_assign(p):
    'expr : LIST LPAREN assignment_list RPAREN EQUALS expr'
    p[0] = ast.ListAssignment(p[3], p[6], lineno=p.lineno(1))

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
    'variable : base_variable'
    p[0] = p[1]

def p_variable_array_offset(p):
    'variable : variable LBRACKET dim_offset RBRACKET'
    p[0] = ast.ArrayOffset(p[1], p[3], lineno=p.lineno(2))

def p_variable_string_offset(p):
    'variable : variable LBRACE expr RBRACE'
    p[0] = ast.StringOffset(p[1], p[3], lineno=p.lineno(2))

def p_variable_object_property(p):
    'variable : variable OBJECT_OPERATOR object_property'
    p[0] = ast.ObjectProperty(p[1], p[3], lineno=p.lineno(2))

def p_variable_function_call(p):
    'variable : namespace_name LPAREN function_call_parameter_list RPAREN'
    p[0] = ast.FunctionCall(p[1], p[3], lineno=p.lineno(2))

def p_variable_class_member_function_call(p):
    'variable : class_name DOUBLE_COLON STRING LPAREN function_call_parameter_list RPAREN'
    p[0] = ast.FunctionCall(ast.ScopeResolution(p[1], p[3], lineno=p.lineno(2)),
                            p[5], lineno=p.lineno(3))

def p_variable_method_call(p):
    'variable : variable OBJECT_OPERATOR object_property LPAREN function_call_parameter_list RPAREN'
    p[0] = ast.MethodCall(p[1], p[3], p[5], lineno=p.lineno(2))

def p_base_variable(p):
    '''base_variable : DOLLAR base_variable
                     | compound_variable'''
    # todo: static_member
    if len(p) == 3:
        p[0] = ast.Variable(p[2], lineno=p.lineno(1))
    else:
        p[0] = p[1]

def p_compound_variable(p):
    '''compound_variable : VARIABLE
                         | DOLLAR LBRACE expr RBRACE'''
    if len(p) == 2:
        p[0] = ast.Variable(p[1], lineno=p.lineno(1))
    else:
        p[0] = ast.Variable(p[3], lineno=p.lineno(1))

def p_dim_offset(p):
    '''dim_offset : expr
                  | empty'''
    p[0] = p[1]

def p_object_property(p):
    '''object_property : variable_name
                       | object_dim_list'''
    p[0] = p[1]

def p_object_dim_list_variable(p):
    'object_dim_list : VARIABLE'
    p[0] = ast.Variable(p[1], lineno=p.lineno(1))

def p_object_dim_list_array_offset(p):
    'object_dim_list : object_dim_list LBRACKET dim_offset RBRACKET'
    p[0] = ast.ArrayOffset(p[1], p[3], lineno=p.lineno(2))

def p_object_dim_list_string_offset(p):
    'object_dim_list : object_dim_list LBRACE expr RBRACE'
    p[0] = ast.StringOffset(p[1], p[3], lineno=p.lineno(2))

def p_variable_name(p):
    '''variable_name : STRING
                     | LBRACE expr RBRACE'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = p[2]

def p_expr_scalar(p):
    'expr : scalar'
    p[0] = p[1]

def p_expr_array(p):
    'expr : ARRAY LPAREN array_pair_list RPAREN'
    p[0] = ast.Array(p[3], lineno=p.lineno(1))

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
        p[0] = p[1] + [ast.ArrayElement(None, p[4], True, lineno=p.lineno(2))]
    elif len(p) == 4:
        p[0] = p[1] + [ast.ArrayElement(None, p[3], False, lineno=p.lineno(2))]
    elif len(p) == 3:
        p[0] = [ast.ArrayElement(None, p[2], True, lineno=p.lineno(1))]
    else:
        p[0] = [ast.ArrayElement(None, p[1], False, lineno=p.lineno(1))]

def p_non_empty_array_pair_list_pair(p):
    '''non_empty_array_pair_list : non_empty_array_pair_list COMMA expr DOUBLE_ARROW AND variable
                                 | non_empty_array_pair_list COMMA expr DOUBLE_ARROW expr
                                 | expr DOUBLE_ARROW AND variable
                                 | expr DOUBLE_ARROW expr'''
    if len(p) == 7:
        p[0] = p[1] + [ast.ArrayElement(p[3], p[6], True, lineno=p.lineno(2))]
    elif len(p) == 6:
        p[0] = p[1] + [ast.ArrayElement(p[3], p[5], False, lineno=p.lineno(2))]
    elif len(p) == 5:
        p[0] = [ast.ArrayElement(p[1], p[4], True, lineno=p.lineno(2))]
    else:
        p[0] = [ast.ArrayElement(p[1], p[3], False, lineno=p.lineno(2))]

def p_possible_comma(p):
    '''possible_comma : empty
                      | COMMA'''
    pass

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
        p[0] = ast.Parameter(p[1], False, lineno=p.lineno(1))
    else:
        p[0] = ast.Parameter(p[2], True, lineno=p.lineno(1))

def p_expr_assign_op(p):
    '''expr : variable PLUS_EQUAL expr
            | variable MINUS_EQUAL expr
            | variable MUL_EQUAL expr
            | variable DIV_EQUAL expr
            | variable CONCAT_EQUAL expr
            | variable MOD_EQUAL expr
            | variable AND_EQUAL expr
            | variable OR_EQUAL expr
            | variable XOR_EQUAL expr
            | variable SL_EQUAL expr
            | variable SR_EQUAL expr'''
    p[0] = ast.AssignOp(p[2], p[1], p[3], lineno=p.lineno(2))

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
    p[0] = ast.BinaryOp(p[2], p[1], p[3], lineno=p.lineno(2))

def p_expr_unary_op(p):
    '''expr : PLUS expr
            | MINUS expr
            | NOT expr
            | BOOLEAN_NOT expr'''
    p[0] = ast.UnaryOp(p[1], p[2], lineno=p.lineno(1))

def p_expr_ternary_op(p):
    'expr : expr QUESTION expr COLON expr'
    p[0] = ast.TernaryOp(p[1], p[3], p[5], lineno=p.lineno(2))

def p_expr_pre_incdec(p):
    '''expr : INC variable
            | DEC variable'''
    p[0] = ast.PreIncDecOp(p[1], p[2], lineno=p.lineno(1))

def p_expr_post_incdec(p):
    '''expr : variable INC
            | variable DEC'''
    p[0] = ast.PostIncDecOp(p[2], p[1], lineno=p.lineno(2))

def p_expr_cast(p):
    '''expr : INT_CAST expr
            | DOUBLE_CAST expr
            | STRING_CAST expr
            | ARRAY_CAST expr
            | OBJECT_CAST expr
            | BOOL_CAST expr
            | UNSET_CAST expr'''
    p[0] = ast.Cast(p[1].strip('() \t'), p[2], lineno=p.lineno(1))

def p_expr_isset(p):
    'expr : ISSET LPAREN isset_variables RPAREN'
    p[0] = ast.IsSet(p[3], lineno=p.lineno(1))

def p_isset_variables(p):
    '''isset_variables : isset_variables COMMA variable
                       | variable'''
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = [p[1]]

def p_expr_empty(p):
    'expr : EMPTY LPAREN expr RPAREN'
    p[0] = ast.Empty(p[3], lineno=p.lineno(1))

def p_expr_eval(p):
    'expr : EVAL LPAREN expr RPAREN'
    p[0] = ast.Eval(p[3], lineno=p.lineno(1))

def p_expr_include(p):
    'expr : INCLUDE expr'
    p[0] = ast.Include(p[2], False, lineno=p.lineno(1))

def p_expr_include_once(p):
    'expr : INCLUDE_ONCE expr'
    p[0] = ast.Include(p[2], True, lineno=p.lineno(1))

def p_expr_require(p):
    'expr : REQUIRE expr'
    p[0] = ast.Require(p[2], False, lineno=p.lineno(1))

def p_expr_require_once(p):
    'expr : REQUIRE_ONCE expr'
    p[0] = ast.Require(p[2], True, lineno=p.lineno(1))

def p_expr_exit(p):
    '''expr : EXIT
            | EXIT LPAREN RPAREN
            | EXIT LPAREN expr RPAREN'''
    if len(p) == 5:
        p[0] = ast.Exit(p[3], lineno=p.lineno(1))
    else:
        p[0] = ast.Exit(None, lineno=p.lineno(1))

def p_expr_print(p):
    'expr : PRINT expr'
    p[0] = ast.Print(p[2], lineno=p.lineno(1))

def p_expr_silence(p):
    'expr : AT expr'
    p[0] = ast.Silence(p[2], lineno=p.lineno(1))

def p_expr_group(p):
    'expr : LPAREN expr RPAREN'
    p[0] = p[2]

def p_scalar(p):
    '''scalar : common_scalar
              | QUOTE encaps_list QUOTE
              | START_HEREDOC encaps_list END_HEREDOC'''
    if len(p) == 4:
        p[0] = p[2]
    else:
        p[0] = p[1]

def p_scalar_string_varname(p):
    'scalar : STRING_VARNAME'
    p[0] = ast.Variable('$' + p[1], lineno=p.lineno(1))

def p_scalar_namespace_name(p):
    'scalar : namespace_name'
    p[0] = ast.Constant(p[1], lineno=p.lineno(1))

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

def p_common_scalar_magic_line(p):
    'common_scalar : LINE'
    p[0] = ast.MagicConstant(p[1], 'TODO', lineno=p.lineno(1))

def p_common_scalar_magic_file(p):
    'common_scalar : FILE'
    p[0] = ast.MagicConstant(p[1], 'TODO', lineno=p.lineno(1))

def p_common_scalar_magic_dir(p):
    'common_scalar : DIR'
    p[0] = ast.MagicConstant(p[1], 'TODO', lineno=p.lineno(1))

def p_common_scalar_magic_class(p):
    'common_scalar : CLASS_C'
    p[0] = ast.MagicConstant(p[1], 'TODO', lineno=p.lineno(1))

def p_common_scalar_magic_method(p):
    'common_scalar : METHOD_C'
    p[0] = ast.MagicConstant(p[1], 'TODO', lineno=p.lineno(1))

def p_common_scalar_magic_func(p):
    'common_scalar : FUNC_C'
    p[0] = ast.MagicConstant(p[1], 'TODO', lineno=p.lineno(1))

def p_common_scalar_magic_ns(p):
    'common_scalar : NS_C'
    p[0] = ast.MagicConstant(p[1], 'TODO', lineno=p.lineno(1))

def p_static_scalar(p):
    '''static_scalar : common_scalar
                     | QUOTE ENCAPSED_AND_WHITESPACE QUOTE'''
    if len(p) == 4:
        p[0] = p[2]
    else:
        p[0] = p[1]

def p_static_scalar_namespace_name(p):
    'static_scalar : namespace_name'
    p[0] = ast.Constant(p[1], lineno=p.lineno(1))

def p_static_scalar_unary_op(p):
    '''static_scalar : PLUS static_scalar
                     | MINUS static_scalar'''
    p[0] = ast.UnaryOp(p[1], p[2], lineno=p.lineno(1))

def p_static_scalar_array(p):
    'static_scalar : ARRAY LPAREN static_array_pair_list RPAREN'
    p[0] = ast.Array(p[3], lineno=p.lineno(1))

def p_static_array_pair_list(p):
    '''static_array_pair_list : empty
                              | static_non_empty_array_pair_list possible_comma'''
    if len(p) == 2:
        p[0] = []
    else:
        p[0] = p[1]

def p_static_non_empty_array_pair_list_item(p):
    '''static_non_empty_array_pair_list : static_non_empty_array_pair_list COMMA static_scalar
                                        | static_scalar'''
    if len(p) == 4:
        p[0] = p[1] + [ast.ArrayElement(None, p[3], False, lineno=p.lineno(2))]
    else:
        p[0] = [ast.ArrayElement(None, p[1], False, lineno=p.lineno(1))]

def p_static_non_empty_array_pair_list_pair(p):
    '''static_non_empty_array_pair_list : static_non_empty_array_pair_list COMMA static_scalar DOUBLE_ARROW static_scalar
                                        | static_scalar DOUBLE_ARROW static_scalar'''
    if len(p) == 6:
        p[0] = p[1] + [ast.ArrayElement(p[3], p[5], False, lineno=p.lineno(2))]
    else:
        p[0] = [ast.ArrayElement(p[1], p[3], False, lineno=p.lineno(2))]

def p_namespace_name(p):
    '''namespace_name : namespace_name NS_SEPARATOR STRING
                      | STRING'''
    if len(p) == 4:
        p[0] = p[1] + p[2] + p[3]
    else:
        p[0] = p[1]

def p_encaps_list(p):
    '''encaps_list : encaps_list encaps_var
                   | encaps_list ENCAPSED_AND_WHITESPACE
                   | empty'''
    if len(p) == 3:
        if p[1] == '':
            p[0] = p[2]
        else:
            p[0] = ast.BinaryOp('.', p[1], p[2], lineno=p.lineno(2))
    else:
        p[0] = ''

def p_encaps_var(p):
    'encaps_var : VARIABLE'
    p[0] = ast.Variable(p[1], lineno=p.lineno(1))

def p_encaps_var_array_offset(p):
    'encaps_var : VARIABLE LBRACKET encaps_var_offset RBRACKET'
    p[0] = ast.ArrayOffset(ast.Variable(p[1], lineno=p.lineno(1)), p[3],
                           lineno=p.lineno(2))

def p_encaps_var_object_property(p):
    'encaps_var : VARIABLE OBJECT_OPERATOR STRING'
    p[0] = ast.ObjectProperty(ast.Variable(p[1], lineno=p.lineno(1)), p[3],
                              lineno=p.lineno(2))

def p_encaps_var_dollar_curly_expr(p):
    'encaps_var : DOLLAR_OPEN_CURLY_BRACES expr RBRACE'
    p[0] = p[2]

def p_encaps_var_dollar_curly_array_offset(p):
    'encaps_var : DOLLAR_OPEN_CURLY_BRACES STRING_VARNAME LBRACKET expr RBRACKET RBRACE'
    p[0] = ast.ArrayOffset(ast.Variable('$' + p[2], lineno=p.lineno(2)), p[4],
                           lineno=p.lineno(3))

def p_encaps_var_curly_variable(p):
    'encaps_var : CURLY_OPEN variable RBRACE'
    p[0] = p[2]

def p_encaps_var_offset_string(p):
    'encaps_var_offset : STRING'
    p[0] = p[1]

def p_encaps_var_offset_num_string(p):
    'encaps_var_offset : NUM_STRING'
    p[0] = int(p[1])

def p_encaps_var_offset_variable(p):
    'encaps_var_offset : VARIABLE'
    p[0] = ast.Variable(p[1], lineno=p.lineno(1))

def p_semi(p):
    '''semi : SEMI
            | CLOSE_TAG'''
    pass

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
