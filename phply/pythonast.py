import phpast as php
import ast as py

needs_strtok = False
needs_re_import = False

python_re_import_ast = py.Import(names=[py.alias(name='re', asname=None)])

python_strtok_ast = py.Module(body=[
    py.FunctionDef(name='strtok', args=py.arguments(args=[py.Name(id='the_string', ctx=py.Param()),
                                                          py.Name(id='the_separator', ctx=py.Param())],
                                                    vararg=None, kwarg=None, defaults=[]), body=[
        py.Expr(value=py.Str(
            s='\\n    Return the first token in the string defined by the separator.\\n    ')),
        py.Assign(targets=[py.Name(id='the_token', ctx=py.Store())],
                  value=py.Name(id='False', ctx=py.Load())),
        py.Assign(targets=[py.Name(id='next_idx', ctx=py.Store())], value=py.Num(n=0)),
        py.While(test=py.BoolOp(op=py.And(),
                                values=[
                                    py.UnaryOp(
                                        op=py.Not(),
                                        operand=py.Name(
                                            id='the_token',
                                            ctx=py.Load())),
                                    py.Name(
                                        id='the_string',
                                        ctx=py.Load())]),
                 body=[py.Assign(targets=[
                     py.Name(id='next_idx',
                             ctx=py.Store())],
                     value=py.Call(
                         func=py.Attribute(
                             value=py.Subscript(
                                 value=py.Name(
                                     id='the_string',
                                     ctx=py.Load()),
                                 slice=py.Slice(
                                     lower=py.Name(
                                         id='next_idx',
                                         ctx=py.Load()),
                                     upper=None,
                                     step=None),
                                 ctx=py.Load()),
                             attr='find',
                             ctx=py.Load()),
                         args=[
                             py.Name(
                                 id='the_separator',
                                 ctx=py.Load())],
                         keywords=[],
                         starargs=None,
                         kwargs=None)),
                     py.If(test=py.Compare(
                         left=py.BinOp(
                             left=py.Name(
                                 id='next_idx',
                                 ctx=py.Load()),
                             op=py.Add(),
                             right=py.Num(
                                 n=1)),
                         ops=[py.Lt()],
                         comparators=[
                             py.Call(
                                 func=py.Name(
                                     id='len',
                                     ctx=py.Load()),
                                 args=[
                                     py.Name(
                                         id='the_string',
                                         ctx=py.Load())],
                                 keywords=[],
                                 starargs=None,
                                 kwargs=None)]), body=[py.If(test=py.Compare(left=py.Name(
                         id='next_idx',
                         ctx=py.Load()), ops=[
                         py.Lt()], comparators=[
                         py.Num(
                             n=0)]), body=[py.Assign(
                         targets=[
                             py.Name(
                                 id='next_idx',
                                 ctx=py.Store())],
                         value=py.Call(
                             func=py.Name(
                                 id='len',
                                 ctx=py.Load()),
                             args=[
                                 py.Name(
                                     id='the_string',
                                     ctx=py.Load())],
                             keywords=[],
                             starargs=None,
                             kwargs=None))], orelse=[]), py.Assign(targets=[py.Name(
                         id='the_token',
                         ctx=py.Store())], value=py.Subscript(value=py.Name(
                         id='the_string',
                         ctx=py.Load()),
                         slice=py.Slice(
                             lower=py.Num(
                                 n=0),
                             upper=py.Name(
                                 id='next_idx',
                                 ctx=py.Load()),
                             step=None),
                         ctx=py.Load())),
                         py.Assign(
                             targets=[
                                 py.Name(
                                     id='the_string',
                                     ctx=py.Store())],
                             value=py.Subscript(
                                 value=py.Name(
                                     id='the_string',
                                     ctx=py.Load()),
                                 slice=py.Slice(
                                     lower=py.BinOp(
                                         left=py.Name(
                                             id='next_idx',
                                             ctx=py.Load()),
                                         op=py.Add(),
                                         right=py.Num(
                                             n=1)),
                                     upper=None,
                                     step=None),
                                 ctx=py.Load())),
                         py.If(
                             test=py.Name(
                                 id='the_token',
                                 ctx=py.Load()),
                             body=[
                                 py.Break()],
                             orelse=[])],
                         orelse=[py.Assign(
                             targets=[
                                 py.Name(
                                     id='the_token',
                                     ctx=py.Store())],
                             value=py.Name(
                                 id='False',
                                 ctx=py.Load())),
                             py.Assign(
                                 targets=[
                                     py.Name(
                                         id='the_string',
                                         ctx=py.Store())],
                                 value=py.Str(
                                     s=''))])],
                 orelse=[]),
        py.Return(value=py.Tuple(
            elts=[py.Name(id='the_string', ctx=py.Load()), py.Name(id='the_token', ctx=py.Load())],
            ctx=py.Load()))], decorator_list=[])])

unary_ops = {
    '~': py.Invert,
    '!': py.Not,
    '+': py.UAdd,
    '-': py.USub,
}

bool_ops = {
    '&&': py.And,
    '||': py.Or,
    'and': py.And,
    'or': py.Or,
}

cmp_ops = {
    '!=': py.NotEq,
    '!==': py.NotEq,
    '<>': py.NotEq,
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

casts = {
    'double': 'float',
    'string': 'str',
    'array': 'list',
}


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

    if isinstance(node, php.Array):
        if node.nodes:
            if node.nodes[0].key is not None:
                keys = []
                values = []
                for elem in node.nodes:
                    keys.append(from_phpast(elem.key))
                    values.append(from_phpast(elem.value))
                return py.Dict(keys, values, **pos(node))
            else:
                return py.List([from_phpast(x.value) for x in node.nodes],
                               py.Load(**pos(node)),
                               **pos(node))
        else:
            return py.List([], py.Load(**pos(node)), **pos(node))

    if isinstance(node, php.InlineHTML):
        args = [py.Str(node.data, **pos(node))]
        return py.Call(py.Name('inline_html',
                               py.Load(**pos(node)),
                               **pos(node)),
                       args, [], None, None,
                       **pos(node))

    if isinstance(node, php.Echo):
        return py.Call(py.Name('echo', py.Load(**pos(node)),
                               **pos(node)),
                       map(from_phpast, node.nodes),
                       [], None, None,
                       **pos(node))

    if isinstance(node, php.Print):
        return py.Print(None, [from_phpast(node.node)], True, **pos(node))

    if isinstance(node, php.Exit):
        args = []
        if node.expr is not None:
            args.append(from_phpast(node.expr))
        return py.Raise(py.Call(py.Name('Exit', py.Load(**pos(node)),
                                        **pos(node)),
                                args, [], None, None, **pos(node)),
                        None, None, **pos(node))

    if isinstance(node, php.Return):
        if node.node is None:
            return py.Return(None, **pos(node))
        else:
            return py.Return(from_phpast(node.node), **pos(node))

    if isinstance(node, php.Break):
        assert node.node is None, 'level on break not supported'
        return py.Break(**pos(node))

    if isinstance(node, php.Continue):
        assert node.node is None, 'level on continue not supported'
        return py.Continue(**pos(node))

    if isinstance(node, php.Silence):
        return from_phpast(node.expr)

    if isinstance(node, php.Block):
        return from_phpast(php.If(1, node, [], None, lineno=node.lineno))

    if isinstance(node, php.Unset):
        return py.Delete(map(from_phpast, node.nodes), **pos(node))

    if isinstance(node, php.IsSet) and len(node.nodes) == 1:
        if isinstance(node.nodes[0], php.ArrayOffset):
            return py.Compare(from_phpast(node.nodes[0].expr),
                              [py.In(**pos(node))],
                              [from_phpast(node.nodes[0].node)],
                              **pos(node))
        if isinstance(node.nodes[0], php.ObjectProperty):
            return py.Call(py.Name('hasattr', py.Load(**pos(node)),
                                   **pos(node)),
                           [from_phpast(node.nodes[0].node),
                            from_phpast(node.nodes[0].name)],
                           [], None, None, **pos(node))
        if isinstance(node.nodes[0], php.Variable):
            return py.Compare(py.Str(node.nodes[0].name[1:], **pos(node)),
                              [py.In(**pos(node))],
                              [py.Call(py.Name('vars', py.Load(**pos(node)),
                                               **pos(node)),
                                       [], [], None, None, **pos(node))],
                              **pos(node))
        return py.Compare(from_phpast(node.nodes[0]),
                          [py.IsNot(**pos(node))],
                          [py.Name('None', py.Load(**pos(node)), **pos(node))],
                          **pos(node))

    if isinstance(node, php.Empty):
        return from_phpast(php.UnaryOp('!',
                                       php.BinaryOp('&&',
                                                    php.IsSet([node.expr],
                                                              lineno=node.lineno),
                                                    node.expr,
                                                    lineno=node.lineno),
                                       lineno=node.lineno))

    if isinstance(node, php.Assignment):
        if (isinstance(node.node, php.ArrayOffset)
            and node.node.expr is None):
            return py.Call(py.Attribute(from_phpast(node.node.node),
                                        'append', py.Load(**pos(node)),
                                        **pos(node)),
                           [from_phpast(node.expr)],
                           [], None, None, **pos(node))
        if (isinstance(node.node, php.ObjectProperty)
            and isinstance(node.node.name, php.BinaryOp)):
            return to_stmt(py.Call(py.Name('setattr', py.Load(**pos(node)),
                                           **pos(node)),
                                   [from_phpast(node.node.node),
                                    from_phpast(node.node.name),
                                    from_phpast(node.expr)],
                                   [], None, None, **pos(node)))
        return py.Assign([store(from_phpast(node.node))],
                         from_phpast(node.expr),
                         **pos(node))

    if isinstance(node, php.ListAssignment):
        return py.Assign([py.Tuple(map(store, map(from_phpast, node.nodes)),
                                   py.Store(**pos(node)),
                                   **pos(node))],
                         from_phpast(node.expr),
                         **pos(node))

    if isinstance(node, php.AssignOp):
        return from_phpast(php.Assignment(node.left,
                                          php.BinaryOp(node.op[:-1],
                                                       node.left,
                                                       node.right,
                                                       lineno=node.lineno),
                                          False,
                                          lineno=node.lineno))

    if isinstance(node, (php.PreIncDecOp, php.PostIncDecOp)):
        return from_phpast(php.Assignment(node.expr,
                                          php.BinaryOp(node.op[0],
                                                       node.expr,
                                                       1,
                                                       lineno=node.lineno),
                                          False,
                                          lineno=node.lineno))

    if isinstance(node, php.ArrayOffset):
        return py.Subscript(from_phpast(node.node),
                            py.Index(from_phpast(node.expr), **pos(node)),
                            py.Load(**pos(node)),
                            **pos(node))

    if isinstance(node, php.ObjectProperty):
        if isinstance(node.name, (php.Variable, php.BinaryOp)):
            return py.Call(py.Name('getattr', py.Load(**pos(node)),
                                   **pos(node)),
                           [from_phpast(node.node),
                            from_phpast(node.name)],
                           [], None, None, **pos(node))
        return py.Attribute(from_phpast(node.node),
                            node.name,
                            py.Load(**pos(node)),
                            **pos(node))

    if isinstance(node, php.Constant):
        name = node.name
        if name.lower() == 'true': name = 'True'
        if name.lower() == 'false': name = 'False'
        if name.lower() == 'null': name = 'None'
        return py.Name(name, py.Load(**pos(node)), **pos(node))

    if isinstance(node, php.Variable):
        name = node.name[1:]
        if name == 'this': name = 'self'
        return py.Name(name, py.Load(**pos(node)), **pos(node))

    if isinstance(node, php.Global):
        return py.Global([var.name[1:] for var in node.nodes], **pos(node))

    if isinstance(node, php.Include):
        once = py.Name('True' if node.once else 'False',
                       py.Load(**pos(node)),
                       **pos(node))
        return py.Call(py.Name('include', py.Load(**pos(node)),
                               **pos(node)),
                       [from_phpast(node.expr), once],
                       [], None, None, **pos(node))

    if isinstance(node, php.Require):
        once = py.Name('True' if node.once else 'False',
                       py.Load(**pos(node)),
                       **pos(node))
        return py.Call(py.Name('require', py.Load(**pos(node)),
                               **pos(node)),
                       [from_phpast(node.expr), once],
                       [], None, None, **pos(node))

    if isinstance(node, php.UnaryOp):
        op = unary_ops.get(node.op)
        assert op is not None, "unknown unary operator: '%s'" % node.op
        op = op(**pos(node))
        return py.UnaryOp(op, from_phpast(node.expr), **pos(node))

    if isinstance(node, php.BinaryOp):
        if node.op == '.':
            pattern, pieces = build_format(node.left, node.right)
            if pieces:
                return py.BinOp(py.Str(pattern, **pos(node)),
                                py.Mod(**pos(node)),
                                py.Tuple(map(from_phpast, pieces),
                                         py.Load(**pos(node)),
                                         **pos(node)),
                                **pos(node))
            else:
                return py.Str(pattern % (), **pos(node))
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

    if isinstance(node, php.TernaryOp):
        return py.IfExp(from_phpast(node.expr),
                        from_phpast(node.iftrue),
                        from_phpast(node.iffalse),
                        **pos(node))

    if isinstance(node, php.Cast):
        return py.Call(py.Name(casts.get(node.type, node.type),
                               py.Load(**pos(node)),
                               **pos(node)),
                       [from_phpast(node.expr)],
                       [], None, None, **pos(node))

    if isinstance(node, php.If):
        or_else = []
        # We handle else first, and then elseifs in revers, then If because each preceding if/elif we create
        # will hold an internal cascaded nested if/else tree down the line. We really *should* support elif, but
        # this works for now -- just looks ugly and isn't amazingly maintainable/readable.
        if node.else_:
            for else_ in map(from_phpast, deblock(node.else_.node)):
                or_else.append(to_stmt(else_))
        for elseif in reversed(node.elseifs):
            or_else = [py.If(from_phpast(elseif.expr),
                            map(to_stmt, map(from_phpast, deblock(elseif.node))),
                            or_else, **pos(node))]
        return py.If(from_phpast(node.expr),
                     map(to_stmt, map(from_phpast, deblock(node.node))),
                     or_else, **pos(node))

    if isinstance(node, php.For):
        assert node.test is None or len(node.test) == 1, \
            'only a single test is supported in for-loops'
        return from_phpast(php.Block((node.start or [])
                                     + [php.While(node.test[0] if node.test else 1,
                                                  php.Block(deblock(node.node)
                                                            + (node.count or []),
                                                            lineno=node.lineno),
                                                  lineno=node.lineno)],
                                     lineno=node.lineno))

    if isinstance(node, php.Foreach):
        if node.keyvar is None:
            target = py.Name(node.valvar.name[1:], py.Store(**pos(node)),
                             **pos(node))
        else:
            target = py.Tuple([py.Name(node.keyvar.name[1:],
                                       py.Store(**pos(node))),
                               py.Name(node.valvar.name[1:],
                                       py.Store(**pos(node)))],
                              py.Store(**pos(node)), **pos(node))
        return py.For(target, from_phpast(node.expr),
                      map(to_stmt, map(from_phpast, deblock(node.node))),
                      [], **pos(node))

    if isinstance(node, php.While):
        return py.While(from_phpast(node.expr),
                        map(to_stmt, map(from_phpast, deblock(node.node))),
                        [], **pos(node))

    if isinstance(node, php.DoWhile):
        condition = php.If(php.UnaryOp('!', node.expr, lineno=node.lineno),
                           php.Break(None, lineno=node.lineno),
                           [], None, lineno=node.lineno)
        return from_phpast(php.While(1,
                                     php.Block(deblock(node.node)
                                               + [condition],
                                               lineno=node.lineno),
                                     lineno=node.lineno))

    if isinstance(node, php.Try):
        return py.TryExcept(map(to_stmt, map(from_phpast, node.nodes)),
                            [py.ExceptHandler(py.Name(catch.class_,
                                                      py.Load(**pos(node)),
                                                      **pos(node)),
                                              store(from_phpast(catch.var)),
                                              map(to_stmt, map(from_phpast, catch.nodes)),
                                              **pos(node))
                             for catch in node.catches],
                            [],
                            **pos(node))

    if isinstance(node, php.Throw):
        return py.Raise(from_phpast(node.node), None, None, **pos(node))

    if isinstance(node, php.Function):
        args = []
        defaults = []
        for param in node.params:
            args.append(py.Name(param.name[1:],
                                py.Param(**pos(node)),
                                **pos(node)))
            if param.default is not None:
                defaults.append(from_phpast(param.default))
        body = map(to_stmt, map(from_phpast, node.nodes))
        if not body: body = [py.Pass(**pos(node))]
        return py.FunctionDef(node.name,
                              py.arguments(args, None, None, defaults),
                              body, [], **pos(node))

    if isinstance(node, php.Method):
        args = []
        defaults = []
        decorator_list = []
        if 'static' in node.modifiers:
            decorator_list.append(py.Name('classmethod',
                                          py.Load(**pos(node)),
                                          **pos(node)))
            args.append(py.Name('cls', py.Param(**pos(node)), **pos(node)))
        else:
            args.append(py.Name('self', py.Param(**pos(node)), **pos(node)))
        for param in node.params:
            args.append(py.Name(param.name[1:],
                                py.Param(**pos(node)),
                                **pos(node)))
            if param.default is not None:
                defaults.append(from_phpast(param.default))
        body = map(to_stmt, map(from_phpast, node.nodes))
        if not body: body = [py.Pass(**pos(node))]
        return py.FunctionDef(node.name,
                              py.arguments(args, None, None, defaults),
                              body, decorator_list, **pos(node))

    if isinstance(node, php.Class):
        name = node.name
        bases = []
        extends = node.extends or 'object'
        bases.append(py.Name(extends, py.Load(**pos(node)), **pos(node)))
        body = map(to_stmt, map(from_phpast, node.nodes))
        for stmt in body:
            if (isinstance(stmt, py.FunctionDef)
                and stmt.name in (name, '__construct')):
                stmt.name = '__init__'
        if not body: body = [py.Pass(**pos(node))]
        return py.ClassDef(name, bases, body, [], **pos(node))

    if isinstance(node, (php.ClassConstants, php.ClassVariables)):
        assert len(node.nodes) == 1, \
            'only one class-level assignment supported per line'
        if isinstance(node.nodes[0], php.ClassConstant):
            name = php.Constant(node.nodes[0].name, lineno=node.lineno)
        else:
            name = php.Variable(node.nodes[0].name, lineno=node.lineno)
        initial = node.nodes[0].initial
        if initial is None:
            initial = php.Constant('None', lineno=node.lineno)
        return py.Assign([store(from_phpast(name))],
                         from_phpast(initial),
                         **pos(node))

    if isinstance(node, (php.FunctionCall, php.New)):
        if isinstance(node.name, basestring):
            global needs_re_import
            if node.name == 'explode':
                args, _ = build_args(node.params)
                all_args = [args[0]]
                if len(args) > 2:
                    all_args.append(args[2])
                return py.Call(func=py.Attribute(value=args[1],
                                                 attr='split', ctx=py.Load()),
                               args=all_args, keywords=[],
                               starargs=None,
                               kwargs=None)
            elif node.name == 'implode':
                args, kwargs = build_args(node.params)
                return py.Call(func=py.Attribute(value=args[0],
                                                 attr='join', ctx=py.Load()),
                               args=[args[1]], keywords=[],
                               starargs=None,
                               kwargs=None)
            elif node.name == 'trim':
                args, kwargs = build_args(node.params)
                call_args = []
                if len(args) > 1:
                    call_args.append(args[1])
                return py.Call(func=py.Attribute(value=args[0],
                                                 attr='strip', ctx=py.Load()),
                               args=call_args, keywords=kwargs,
                               starargs=None,
                               kwargs=None)
            elif node.name == 'strtok':
                global needs_strtok
                needs_strtok = True
                args, kwargs = build_args(node.params)
                return py.Call(func=py.Name(id='strtok', ctx=py.Load()),
                               args=args, keywords=kwargs, starargs=None,
                               kwargs=None)
            elif node.name == 'strtolower':
                args, _ = build_args(node.params)
                return py.Call(func=py.Attribute(value=args[0],
                                                 attr='lower', ctx=py.Load()),
                               args=[], keywords=[],
                               starargs=None,
                               kwargs=None)
            elif node.name == 'strtoupper':
                args, _ = build_args(node.params)
                return py.Call(func=py.Attribute(value=args[0],
                                                 attr='upper', ctx=py.Load()),
                               args=[], keywords=[],
                               starargs=None,
                               kwargs=None)
            elif node.name == 'preg_replace' or node.name == 'preg_replace_callback':
                needs_re_import = True
                args, kwargs = build_args(node.params)
                return py.Call(func=py.Attribute(value=py.Name(id='re', ctx=py.Load()),
                                                 attr='sub', ctx=py.Load()),
                               args=args, keywords=kwargs,
                               starargs=None,
                               kwargs=None)
            elif node.name == 'preg_split':
                needs_re_import = True
                args, kwargs = build_args(node.params)
                return py.Call(func=py.Attribute(value=py.Name(id='re', ctx=py.Load()),
                                                 attr='split', ctx=py.Load()),
                               args=args, keywords=kwargs,
                               starargs=None,
                               kwargs=None)
            elif node.name == 'preg_match':
                needs_re_import = True
                args, kwargs = build_args(node.params)
                return py.Call(func=py.Attribute(value=py.Name(id='re', ctx=py.Load()),
                                                 attr='search', ctx=py.Load()),
                               args=args, keywords=kwargs,
                               starargs=None,
                               kwargs=None)
            elif node.name == 'preg_quote':
                needs_re_import = True
                args, kwargs = build_args(node.params)
                return py.Call(func=py.Attribute(value=py.Name(id='re', ctx=py.Load()),
                                                 attr='escape', ctx=py.Load()),
                               args=args, keywords=kwargs,
                               starargs=None,
                               kwargs=None)
            else:
                if node.name == 'count':
                    node.name = 'len'
                name = py.Name(node.name, py.Load(**pos(node)), **pos(node))
        else:
            name = py.Subscript(py.Call(py.Name('vars', py.Load(**pos(node)),
                                                **pos(node)),
                                        [], [], None, None, **pos(node)),
                                py.Index(from_phpast(node.name), **pos(node)),
                                py.Load(**pos(node)),
                                **pos(node))
        args, kwargs = build_args(node.params)
        return py.Call(name, args, kwargs, None, None, **pos(node))

    if isinstance(node, php.MethodCall):
        args, kwargs = build_args(node.params)
        return py.Call(py.Attribute(from_phpast(node.node),
                                    node.name,
                                    py.Load(**pos(node)),
                                    **pos(node)),
                       args, kwargs, None, None, **pos(node))

    if isinstance(node, php.StaticMethodCall):
        class_ = node.class_
        if class_ == 'self': class_ = 'cls'
        args, kwargs = build_args(node.params)
        return py.Call(py.Attribute(py.Name(class_, py.Load(**pos(node)),
                                            **pos(node)),
                                    node.name,
                                    py.Load(**pos(node)),
                                    **pos(node)),
                       args, kwargs, None, None, **pos(node))

    if isinstance(node, php.StaticProperty):
        class_ = node.node
        name = node.name
        if isinstance(name, php.Variable):
            name = name.name[1:]
        return py.Attribute(py.Name(class_, py.Load(**pos(node)),
                                    **pos(node)),
                            name,
                            py.Load(**pos(node)),
                            **pos(node))
    if isinstance(node, php.Default):
        return None

    if isinstance(node, php.Switch):
        # does not handle no break at the end of the case, and assumes default is last in the order.
        # And like the php.If in this function, we do not optimize up for elif, just cascading nested if/else
        or_else = []
        if len(node.nodes) > 1:
            for case_node in node.nodes[::-1][:-1]:
                node_expr_for_ast = case_node.expr if hasattr(case_node, 'expr') else case_node
                case_ast = from_phpast(node_expr_for_ast)
                if case_ast:
                    case_body_nodes = []
                    for case_body_node in case_node.nodes:
                        if isinstance(case_body_node, (py.Break, php.Break)):
                            if not len(case_body_nodes):  # do not want an empty case/if
                                case_body_nodes.append(py.Pass(**pos(case_body_node)))
                            break
                        case_body_nodes.append(case_body_node)
                    or_else = [
                        py.If(test=py.Compare(left=case_ast, ops=[py.Eq()], comparators=[from_phpast(node.expr)]),
                              body=map(to_stmt, map(from_phpast, case_body_nodes)),
                              orelse=or_else, **pos(node))]
                else:
                    for the_else_node in map(from_phpast, case_node.nodes):
                        if isinstance(the_else_node, (py.Break, php.Break)):
                            if not len(case_node.nodes) > 1:
                                the_else_node = py.Pass(**pos(the_else_node))
                                or_else.append(to_stmt(the_else_node))
                            break
                        or_else.append(to_stmt(the_else_node))
        top_case_ast = from_phpast(node.nodes[0].expr)
        top_body_nodes = []
        for top_body_node in node.nodes[0].nodes:
            if isinstance(top_body_node, (py.Break, php.Break)):
                if not len(top_body_nodes):  # do not want an empty case/if
                    top_body_nodes.append(py.Pass(**pos(top_body_node)))
                break
            top_body_nodes.append(top_body_node)
        return py.If(test=py.Compare(left=top_case_ast, ops=[py.Eq()], comparators=[from_phpast(node.expr)]),
                     body=map(to_stmt, map(from_phpast, top_body_nodes)) or [py.Pass(**pos(node.nodes[0]))],
                     orelse=or_else)
    return py.Call(py.Name('XXX', py.Load(**pos(node)), **pos(node)),
                   [py.Str(str(node), **pos(node))],
                   [], None, None, **pos(node))


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


def build_args(params):
    args = []
    kwargs = []
    for param in params:
        node = from_phpast(param.node)
        if isinstance(node, py.Assign):
            kwargs.append(py.keyword(node.targets[0].id, node.value))
        else:
            args.append(node)
    return args, kwargs


def build_format(left, right):
    if isinstance(left, basestring):
        pattern, pieces = left.replace('%', '%%'), []
    elif isinstance(left, php.BinaryOp) and left.op == '.':
        pattern, pieces = build_format(left.left, left.right)
    else:
        pattern, pieces = '%s', [left]
    if isinstance(right, basestring):
        pattern += right.replace('%', '%%')
    else:
        pattern += '%s'
        pieces.append(right)
    return pattern, pieces
