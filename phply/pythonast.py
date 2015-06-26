import phpast as php
import ast as py

needs_strtok = False
needs_re_import = False
needs_strpos = False

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

class PySwitch(object):
    def process(self, node):
        # does not handle no break at the end of the case, and assumes default is last in the order.
        # And like the php.If in this function, we do not optimize up for elif, just cascading nested if/else
        skip_true = py.Assign(targets=[py.Name(id='skip', ctx=py.Store())], value=py.Name(id='True', ctx=py.Load()))
        skip_false = py.Assign(targets=[py.Name(id='skip', ctx=py.Store())], value=py.Name(id='False', ctx=py.Load()))
        body = []
        or_else = []
        if len(node.nodes) > 1:
            node_groups = []
            for case_idx in xrange(len(node.nodes) - 1):
                cur_case = node.nodes[len(node.nodes) - 1 - case_idx]
                if len(node_groups):
                    cur_node_groups_len = len(node_groups)
                    for stmt_in_case in cur_case.nodes[::-1]:
                        # there is a top-level break statement here, so we will build a new group
                        if isinstance(stmt_in_case, (php.Break, py.Break)):
                            node_groups.insert(0, [cur_case])
                            break
                    # we did not find any top-level break statements, so we will add this case to the current head list
                    if cur_node_groups_len == len(node_groups):
                        node_groups[0].insert(0, cur_case)
                else:
                    # this is the special beginning case
                    node_groups.append([cur_case])
            # if the lengths are the same, treat each case as a single elif (essentially)
            if len(node_groups) == (len(node.nodes) - 1):
                for case_node in node.nodes[::-1][:-1]:
                    node_expr_for_ast = case_node.expr if hasattr(case_node, 'expr') else case_node
                    if isinstance(node_expr_for_ast, list):
                        case_ast = map(from_phpast, node_expr_for_ast)
                    else:
                        case_ast = from_phpast(node_expr_for_ast)
                    case_body_nodes = []
                    for case_body_node in case_node.nodes:
                        if isinstance(case_body_node, (py.Break, php.Break)):
                            if not case_body_nodes:  # do not want an empty case/if
                                case_body_nodes.append(py.Pass(**pos(case_body_node)))
                            break
                        case_body_nodes.append(case_body_node)
                    if_test = py.Name(id='True', ctx=py.Load())
                    if case_ast:
                        if_test = py.Compare(left=case_ast, ops=[py.Eq()], comparators=[from_phpast(node.expr)])
                    inner_body = []
                    if hasattr(case_body_nodes, 'nodes'):
                        for php_body_node in case_body_nodes.nodes:
                            type_thing = from_phpast(php_body_node)
                            if isinstance(type_thing, list):
                                inner_body.extend(type_thing)
                            else:
                                inner_body.append(type_thing)

                    inner_body = map(to_stmt, inner_body) or [py.Pass()]
                    or_else = [
                        py.If(test=if_test,
                              body=inner_body,
                              orelse=or_else, **pos(node))]
            else:
                body.append(skip_false)
                # fold-in each node group to be one massive If BoolOp Or
                for node_group_idx, node_group in enumerate(node_groups):
                    for node_element in node_group:
                        new_if = py.If(test=py.BoolOp(op=py.Or(), values=[py.Name(id='skip', ctx=py.Load())]), orelse=[], body=[])
                        body.append(new_if)
                        # Look for a break
                        if not self.drill(node_element, php.Break, ignore=[php.Switch]):
                            new_if.body.insert(0, skip_false)
                        else:
                            new_if.body.insert(0, skip_true)

                        element_to_ast = node_element.expr if hasattr(node_element, 'expr') else node_element
                        element_as_ast = from_phpast(element_to_ast)
                        if element_as_ast:
                            next_compare = py.Compare(left=from_phpast(node.expr), ops=[py.Eq()],
                                                      comparators=[element_as_ast])
                            new_if.test.values.append(next_compare)
                        elif len(node_group) == 1:
                            # this is the default, and the sole "case" in the group.
                            new_if.test = py.Name(id='True', ctx=py.Load())
                        for idx, stmt_in_case in enumerate(node_element.nodes):
                            if isinstance(stmt_in_case, php.Break):
                                if not idx:
                                    new_if.body.append(py.Pass(**pos(from_phpast(stmt_in_case))))
                                break
                            else:
                                type_thing = from_phpast(stmt_in_case)
                                if isinstance(type_thing, list):
                                    new_if.body.extend(map(to_stmt, type_thing))
                                else:
                                    new_if.body.append(to_stmt(type_thing))
                    # or_else.append(new_if)
                for if_idx, the_if in enumerate(or_else):
                    if if_idx + 1 < len(or_else):
                        the_if.orelse = [or_else[if_idx + 1]]
        if not node.nodes:
            top_case_ast = None
        else:
            top_case_ast = from_phpast(node.nodes[0].expr) if hasattr(node.nodes[0], 'expr') else from_phpast(node)
        top_body_nodes = []
        top_case_has_break = False
        if node.nodes:
            for top_body_node in node.nodes[0].nodes:
                if isinstance(top_body_node, (py.Break, php.Break)):
                    top_case_has_break = True
                    if not len(top_body_nodes):  # do not want an empty case/if
                        top_body_nodes.append(py.Pass(**pos(top_body_node)))
                    break
                top_body_nodes.append(top_body_node)
        if top_case_has_break:
            inner_body = []
            if hasattr(top_body_nodes, 'nodes'):
                for php_body_node in top_body_nodes.nodes:
                    type_thing = from_phpast(php_body_node)
                    if isinstance(type_thing, list):
                        inner_body.extend(type_thing)
                    else:
                        inner_body.append(type_thing)

            inner_body = map(to_stmt, inner_body)
            the_pos = py.Pass()
            if node.nodes:
                the_pos = py.Pass(**pos(node.nodes[0]))
            temp = py.If(test=py.Compare(left=from_phpast(node.expr), ops=[py.Eq()], comparators=[top_case_ast]),
                         body=inner_body or [the_pos],
                         orelse=or_else)
            if not self.drill(top_body_nodes[0], php.Break, ignore=[php.Switch]):
                temp.body.insert(0, skip_false)
            else:
                temp.body.insert(0, skip_true)
            body.insert(1, temp)
        else:
            # Do this: map(to_stmt, map(from_phpast, top_body_nodes))
            # With this: for for
            inner_body = []
            if hasattr(top_body_nodes, 'nodes'):
                for php_body_node in top_body_nodes.nodes:
                    type_thing = from_phpast(php_body_node)
                    if isinstance(type_thing, list):
                        inner_body.extend(type_thing)
                    else:
                        inner_body.append(type_thing)

            inner_body = map(to_stmt, inner_body)
            the_pos = py.Pass()
            if node.nodes:
                the_pos = py.Pass(**pos(node.nodes[0]))
            # if there are any other nodes, fold this one into the top node's logic as a BoolOpOr
            comparators = [top_case_ast] if top_case_ast else []
            first_if = py.If(test=py.Compare(left=from_phpast(node.expr), ops=[py.Eq()], comparators=comparators),
                         body=inner_body or [the_pos],
                         orelse=or_else)

            if not len(top_body_nodes) or not self.drill(top_body_nodes[0], php.Break, ignore=[php.Switch]):
                first_if.body.insert(0, skip_false)
            else:
                first_if.body.insert(0, skip_true)
            body.insert(1, first_if)
        return body

    def drill(self, node, target, ignore):
        if not isinstance(node, target) and hasattr(node, 'nodes'):
            for thing in node.nodes:
                if type(thing) in ignore:
                    continue
                rtn = self.drill(thing, target, ignore)
                if rtn:
                    return rtn
            return False
        elif not isinstance(node, target) and hasattr(node, 'node'):
            rtn = self.drill(node.node, target, ignore)
            if rtn:
                return rtn
            return False
        elif isinstance(node, target):
            return True
        else:
            return False


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
        unary_operand = from_phpast(node.expr)
        # more pythonic, syntactically -- only handling one ops...I do not intend for this to be a full pythonic surgery
        if isinstance(op, py.Not) and isinstance(unary_operand, py.Compare) and len(unary_operand.ops) == 1:
            # Not and In make a NotIn
            if isinstance(unary_operand.ops[0], py.In):
                unary_operand.ops[0] = py.NotIn()
                return unary_operand
            # Not and NotIn make an In
            elif isinstance(unary_operand.ops[0], py.NotIn):
                unary_operand.ops[0] = py.In()
                return unary_operand
        return py.UnaryOp(op, unary_operand, **pos(node))

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
                             map(to_stmt, map(from_phpast, deblock(elseif.node))) or [py.Pass(**pos(elseif))],
                             or_else, **pos(node))]
        node_tree = deblock(node.node)
        map_of_nodes = map(from_phpast, node_tree)
        node_list = []
        for lists in map_of_nodes:
            if isinstance(lists, list):
                node_list.extend(lists)
            else:
                node_list.append(lists)
        the_test = all_the_test = from_phpast(node.expr)
        the_assign = None
        if isinstance(the_test, py.Assign):
            the_assign = the_test
            the_test = py.Name(id=the_assign.targets[0].id, ctx=py.Load())
        elif isinstance(the_test, list):
            the_test = the_test[-1]
        the_if = py.If(the_test,
                     map(to_stmt, node_list) or [py.Pass(**pos(node))],
                     or_else, **pos(node))
        if isinstance(all_the_test, list):
            return [all_the_test, the_if]
        else:
            return [the_assign, the_if] if the_assign else the_if
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
        node_tree = deblock(node.node)
        map_of_nodes = map(from_phpast, node_tree)
        node_list = []
        for lists in map_of_nodes:
            if isinstance(lists, list):
                node_list.extend(lists)
            else:
                node_list.append(lists)
        return py.For(target, from_phpast(node.expr),
                      map(to_stmt, map(from_phpast, node_list)),
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
        as_ast_nodes = []
        for node_to_make_as_ast in node.nodes:
            node_as_ast_return = from_phpast(node_to_make_as_ast)
            if isinstance(node_as_ast_return, list):
                as_ast_nodes.extend(node_as_ast_return)
            else:
                as_ast_nodes.append(node_as_ast_return)
        body = map(to_stmt, as_ast_nodes)
        if not body: body = [py.Pass(**pos(node))]
        return py.FunctionDef(node.name,
                              py.arguments(args, None, None, defaults),
                              body, decorator_list, **pos(node))

    if isinstance(node, php.Class):
        name = node.name
        bases = []
        extends = node.extends or 'object'
        bases.append(py.Name(extends, py.Load(**pos(node)), **pos(node)))
        as_ast_nodes = []
        for node_to_make_as_ast in node.nodes:
            node_as_ast_return = from_phpast(node_to_make_as_ast)
            if isinstance(node_as_ast_return, list):
                as_ast_nodes.extend(node_as_ast_return)
            else:
                as_ast_nodes.append(node_as_ast_return)
        body = map(to_stmt, as_ast_nodes)
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
            if node.name == 'in_array':
                args, _ = build_args(node.params)
                return py.Compare(left=args[0], ops=[py.In()],
                                  comparators=[args[1]], ctx=py.Load())
            elif node.name == 'explode':
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
                elif node.name == 'strcmp':
                    node.name = 'cmp'
                elif node.name == 'strpos':
                    global needs_strpos
                    needs_strpos = True
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
       return PySwitch().process(node)

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

py_strpos_ast = py.FunctionDef(name='strpos', args=py.arguments(args=[py.Name(id='haystack', ctx=py.Param()),
                                                                      py.Name(id='needle', ctx=py.Param()),
                                                                      py.Name(id='offset', ctx=py.Param())],
                                                                vararg=None, kwarg=None, defaults=[py.Num(n=0)]),
                               body=[py.Expr(value=py.Str
                               (s='Return index of needle in haystack, or False if not found.\\n\\n    '
                                  'Note: This is intended to emulate the logic of the PHP version.\\n    ')),
                                     py.Assign(targets=[py.Name(id='the_position', ctx=py.Store())],
                                               value=py.Call(func=py.Attribute(value=py.Name(id='haystack',
                                                                                             ctx=py.Load()),
                                                                               attr='find', ctx=py.Load()),
                                                             args=[py.Name(id='needle', ctx=py.Load()),
                                                                   py.Name(id='offset', ctx=py.Load())],
                                                             keywords=[], starargs=None, kwargs=None)),
                                     py.If(test=py.Compare(left=py.Name(id='the_position', ctx=py.Load()),
                                                           ops=[py.Eq()], comparators=[py.Num(n=-1)]),
                                           body=[py.Assign(targets=[py.Name(id='the_position', ctx=py.Store())],
                                                           value=py.Name(id='False', ctx=py.Load()))], orelse=[]),
                                     py.Return(value=py.Name(id='the_position', ctx=py.Load()))],
                               decorator_list=[])
