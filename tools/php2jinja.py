#!/usr/bin/env python

# php2jinja.py - Converts PHP to Jinja2 templates (experimental)
# Usage: php2jinja.py < input.php > output.html

import sys
sys.path.append('..')

from phply.phplex import lexer
from phply.phpparse import make_parser
from phply.phpast import *

input = sys.stdin
output = sys.stdout

op_map = {
    '&&':  'and',
    '||':  'or',
    '!':   'not',
    '!==': '!=',
    '===': '==',
    '.':   '~',
}

def unparse(nodes):
    result = []
    for node in nodes:
        result.append(unparse_node(node))
    return ''.join(result)

def unparse_node(node, is_expr=False):
    if isinstance(node, (str, int, float)):
        return repr(node)

    if isinstance(node, InlineHTML):
        return str(node.data)

    if isinstance(node, Constant):
        if node.name.lower() == 'null':
            return 'None'
        return str(node.name)

    if isinstance(node, Variable):
        return str(node.name[1:])

    if isinstance(node, Echo):
        return '{{ %s }}' % (''.join(unparse_node(x, True) for x in node.nodes))

    if isinstance(node, (Include, Require)):
        return '{%% include %s -%%}' % (unparse_node(node.expr, True))

    if isinstance(node, Block):
        return ''.join(unparse_node(x) for x in node.nodes)

    if isinstance(node, ArrayOffset):
        return '%s[%s]' % (unparse_node(node.node, True),
                           unparse_node(node.expr, True))

    if isinstance(node, ObjectProperty):
        return '%s.%s' % (unparse_node(node.node, True), node.name)

    if isinstance(node, Array):
        elems = []
        for elem in node.nodes:
            elems.append(unparse_node(elem, True))
        if node.nodes and node.nodes[0].key is not None:
            return '{%s}' % ', '.join(elems)
        else:
            return '[%s]' % ', '.join(elems)

    if isinstance(node, ArrayElement):
        if node.key:
            return '%s: %s' % (unparse_node(node.key, True),
                               unparse_node(node.value, True))
        else:
            return unparse_node(node.value, True)

    if isinstance(node, Assignment):
        if isinstance(node.node, ArrayOffset) and node.node.expr is None:
            return '{%% do %s.append(%s) -%%}' % (unparse_node(node.node.node, None),
                                                 unparse_node(node.expr, True))
        else:
            return '{%% set %s = %s -%%}' % (unparse_node(node.node, True),
                                            unparse_node(node.expr, True))

    if isinstance(node, UnaryOp):
        op = op_map.get(node.op, node.op)
        return '(%s %s)' % (op, unparse_node(node.expr, True))

    if isinstance(node, BinaryOp):
        op = op_map.get(node.op, node.op)
        return '(%s %s %s)' % (unparse_node(node.left, True), op,
                               unparse_node(node.right, True))

    if isinstance(node, TernaryOp):
        return '(%s if %s else %s)' % (unparse_node(node.iftrue, True),
                                       unparse_node(node.expr, True),
                                       unparse_node(node.iffalse, True))

    if isinstance(node, IsSet):
        if len(node.nodes) == 1:
            return '(%s is defined)' % unparse_node(node.nodes[0], True)
        else:
            tests = ['(%s is defined)' % unparse_node(n, True)
                     for n in node.nodes]
            return '(' + ' and '.join(tests) + ')'

    if isinstance(node, Empty):
        return '(not %s)' % (unparse_node(node.expr, True))

    if isinstance(node, Silence):
        return unparse_node(node.expr, True)

    if isinstance(node, Cast):
        filter = ''
        if node.type in ('int', 'float', 'string'):
            filter = '|%s' % node.type
        return '%s%s' % (unparse_node(node.expr, True), filter)

    if isinstance(node, If):
        body = unparse_node(node.node)
        for elseif in node.elseifs:
            body += '{%% elif %s -%%}%s' % (unparse_node(elseif.expr, True),
                                           unparse_node(elseif.node))
        if node.else_:
            body += '{%% else -%%}%s' % (unparse_node(node.else_.node))
        return '{%% if %s -%%}%s{%% endif -%%}' % (unparse_node(node.expr, True),
                                                 body)

    if isinstance(node, While):
        dummy = Foreach(node.expr, None, ForeachVariable('$XXX', False), node.node)
        return unparse_node(dummy)

    if isinstance(node, Foreach):
        var = node.valvar.name[1:]
        if node.keyvar:
            var = '%s, %s' % (node.keyvar.name[1:], var)
        return '{%% for %s in %s -%%}%s{%% endfor -%%}' % (var,
                                                         unparse_node(node.expr, True),
                                                         unparse_node(node.node))

    if isinstance(node, Function):
        name = node.name
        params = []
        for param in node.params:
            params.append(param.name[1:])
            # if param.default is not None:
            #     params.append('%s=%s' % (param.name[1:],
            #                              unparse_node(param.default, True)))
            # else:
            #     params.append(param.name[1:])
        params = ', '.join(params)
        body = '\n    '.join(unparse_node(node) for node in node.nodes)
        return '{%% macro %s(%s) -%%}\n    %s\n{%%- endmacro -%%}\n\n' % (name, params, body)

    if isinstance(node, Return):
        return '{{ %s }}' % unparse_node(node.node, True)

    if isinstance(node, FunctionCall):
        if node.name.endswith('printf'):
            params = [unparse_node(x.node, True) for x in node.params[1:]]
            if is_expr:
                return '%s %% (%s,)' % (unparse_node(node.params[0].node, True),
                                        ', '.join(params))
            else:
                return '{{ %s %% (%s,) }}' % (unparse_node(node.params[0].node, True),
                                              ', '.join(params))
        params = ', '.join(unparse_node(param.node, True)
                           for param in node.params)
        if is_expr:
            return '%s(%s)' % (node.name, params)
        else:
            return '{{ %s(%s) }}' % (node.name, params)

    if isinstance(node, MethodCall):
        params = ', '.join(unparse_node(param.node, True)
                           for param in node.params)
        if is_expr:
            return '%s.%s(%s)' % (unparse_node(node.node, True),
                                  node.name, params)
        else:
            return '{{ %s.%s(%s) }}' % (unparse_node(node.node, True),
                                        node.name, params)

    if is_expr:
        return 'XXX(%r)' % str(node)
    else:
        return '{# XXX %s #}' % node

parser = make_parser()
output.write(unparse(parser.parse(input.read(), lexer=lexer)))
