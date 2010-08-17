import phpast as php
import ast as py

unary_ops = {
    '~': py.Invert,
    '!': py.Not,
    '+': py.UAdd,
    '-': py.USub,
}

bool_ops = {
    '&&': py.And,
    '||': py.Or,
}

cmp_ops = {
    '!=': py.NotEq,
    '!==': py.NotEq,
    '<': py.Lt,
    '<=': py.LtE,
    '==': py.Eq,
    '===': py.Eq,
    '>': py.Gt,
    '>=': py.GtE,
}

binary_ops = {
    '+': py.Add,
    '-': py.Sub,
    '*': py.Mult,
    '/': py.Div,
    '%': py.Mod,
    '<<': py.LShift,
    '>>': py.RShift,
    '|': py.BitOr,
    '&': py.BitAnd,
    '^': py.BitXor,
}

def pos(node):
    return {'lineno': getattr(node, 'lineno', 0), 'col_offset': 0}

def store(name):
    name.ctx = py.Store(**pos(name))
    return name

def deblock(node):
    if isinstance(node, php.Block):
        return node.nodes
    else:
        return [node]

def to_stmt(pynode):
    if not isinstance(pynode, py.stmt):
        pynode = py.Expr(pynode,
                         lineno=pynode.lineno,
                         col_offset=pynode.col_offset)
    return pynode

def from_phpast(node):
    if node is None:
        return py.Pass(**pos(node))

    if isinstance(node, basestring):
        return py.Str(node, **pos(node))

    if isinstance(node, (int, float)):
        return py.Num(node, **pos(node))

    if isinstance(node, php.InlineHTML):
        args = [py.Str(node.data, **pos(node))]
        return py.Call(py.Name('inline_html',
                               py.Load(**pos(node)),
                               **pos(node)),
                       args, [], None, None,
                       **pos(node))

    if isinstance(node, php.Echo):
        args = map(from_phpast, node.nodes)
        return py.Call(py.Name('echo', py.Load(**pos(node)),
                               **pos(node)),
                       args, [], None, None,
                       **pos(node))

    if isinstance(node, php.Print):
        return py.Print(None, [from_phpast(node.node)], True, **pos(node))

    if isinstance(node, php.Exit):
        return py.Raise(py.Call(py.Name('Exit', py.Load(**pos(node)),
                                        **pos(node)),
                                [from_phpast(node.expr)], [], None, None,
                                **pos(node)),
                        None, None, **pos(node))

    if isinstance(node, php.Return):
        return py.Return(from_phpast(node.node), **pos(node))

    if isinstance(node, php.Silence):
        return from_phpast(node.expr)

    if isinstance(node, php.Unset):
        return py.Delete(map(from_phpast, node.nodes), **pos(node))

    if isinstance(node, php.Assignment):
        return py.Assign([store(from_phpast(node.node))],
                         from_phpast(node.expr),
                         **pos(node))

    if isinstance(node, php.ArrayOffset):
        return py.Subscript(from_phpast(node.node),
                            py.Index(from_phpast(node.expr), **pos(node)),
                            py.Load(**pos(node)),
                            **pos(node))

    if isinstance(node, php.Constant):
        name = node.name
        if name.lower() == 'true': name = 'True'
        if name.lower() == 'false': name = 'False'
        if name.lower() == 'null': name = 'None'
        return py.Name(name, py.Load(**pos(node)), **pos(node))

    if isinstance(node, php.Variable):
        return py.Name(node.name[1:], py.Load(**pos(node)), **pos(node))

    if isinstance(node, (php.Include, php.Require)):
        return py.Call(py.Name('execfile', py.Load(**pos(node)),
                               **pos(node)),
                       [from_phpast(node.expr)],
                       [], None, None, **pos(node))

    if isinstance(node, php.UnaryOp):
        op = unary_ops.get(node.op)
        assert op is not None, "unknown unary operator: '%s'" % node.op
        op = op(**pos(node))
        return py.UnaryOp(op, from_phpast(node.expr), **pos(node))

    if isinstance(node, php.BinaryOp):
        if node.op == '.':
            return py.BinOp(py.Str('%s%s', **pos(node)),
                            py.Mod(**pos(node)),
                            py.Tuple([from_phpast(node.left),
                                      from_phpast(node.right)],
                                     py.Load(**pos(node)),
                                     **pos(node)),
                            **pos(node))
        if node.op in bool_ops:
            op = bool_ops[node.op](**pos(node))
            return py.BoolOp(op, [from_phpast(node.left),
                                  from_phpast(node.right)], **pos(node))
        if node.op in cmp_ops:
            op = cmp_ops[node.op](**pos(node))
            return py.Compare(from_phpast(node.left), [op],
                              [from_phpast(node.right)],
                              **pos(node))
        op = binary_ops.get(node.op)
        assert op is not None, "unknown binary operator: '%s'" % node.op
        op = op(**pos(node))
        return py.BinOp(from_phpast(node.left),
                        op,
                        from_phpast(node.right),
                        **pos(node))

    if isinstance(node, php.If):
        orelse = []
        if node.else_:
            for else_ in map(from_phpast, deblock(node.else_.node)):
                orelse.append(to_stmt(else_))
        for elseif in reversed(node.elseifs):
            orelse = [py.If(from_phpast(elseif.expr),
                            map(to_stmt, map(from_phpast, deblock(elseif.node))),
                            orelse, **pos(node))]
        return py.If(from_phpast(node.expr),
                     map(to_stmt, map(from_phpast, deblock(node.node))),
                     orelse, **pos(node))

    if isinstance(node, php.FunctionCall):
        name = node.name
        args = []
        for param in node.params:
            args.append(from_phpast(param.node))
        return py.Call(py.Name(name, py.Load(**pos(node)), **pos(node)),
                       args, [], None, None, **pos(node))

    return py.Call(py.Name('XXX', py.Load(**pos(node)), **pos(node)),
                   [py.Str(str(node), **pos(node))],
                   [], None, None, **pos(node))
