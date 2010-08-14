from phply.phpparse import parser
from phply.phpast import *
import nose.tools

def eq_ast(input, expected):
    output = parser.parse(input)
    print output
    assert len(output) == len(expected)
    for out, exp in zip(output, expected):
        print out, exp
        nose.tools.eq_(out, exp)

def test_inline_html():
    input = 'html <?php // php ?> more html'
    expected = [InlineHTML('html '), InlineHTML('more html')]
    eq_ast(input, expected)

def test_echo():
    input = '<?php echo "hello, world!"; ?>'
    expected = [Echo(["hello, world!"])]
    eq_ast(input, expected)

def test_exit():
    input = '<?php exit; exit(); exit(123); die; die(); die(456); ?>'
    expected = [
        Exit(None), Exit(None), Exit(123),
        Exit(None), Exit(None), Exit(456),
    ]
    eq_ast(input, expected)

def test_isset():
    input = r"""<?php
        isset($a);
        isset($b->c);
        isset($d['e']);
        isset($f, $g);
    ?>"""
    expected = [
        IsSet([Variable('$a')]),
        IsSet([ObjectProperty(Variable('$b'), 'c')]),
        IsSet([ArrayOffset(Variable('$d'), 'e')]),
        IsSet([Variable('$f'), Variable('$g')]),
    ]
    eq_ast(input, expected)

def test_namespace_names():
    input = r"""<?php
        foo;
        bar\baz;
        one\too\tree;
    ?>"""
    expected = [
        Constant(r'foo'),
        Constant(r'bar\baz'),
        Constant(r'one\too\tree'),
    ]
    eq_ast(input, expected)

def test_unary_ops():
    input = r"""<?
        $a = -5;
        $b = +6;
        $c = !$d;
        $e = ~$f;
    ?>"""
    expected = [
        Assignment(Variable('$a'), UnaryOp('-', 5), False),
        Assignment(Variable('$b'), UnaryOp('+', 6), False),
        Assignment(Variable('$c'), UnaryOp('!', Variable('$d')), False),
        Assignment(Variable('$e'), UnaryOp('~', Variable('$f')), False),
    ]
    eq_ast(input, expected)

def test_assignment_ops():
    input = r"""<?
        $a += 5;
        $b -= 6;
        $c .= $d;
        $e ^= $f;
    ?>"""
    expected = [
        AssignOp('+=', Variable('$a'), 5),
        AssignOp('-=', Variable('$b'), 6),
        AssignOp('.=', Variable('$c'), Variable('$d')),
        AssignOp('^=', Variable('$e'), Variable('$f')),
    ]
    eq_ast(input, expected)

def test_object_properties():
    input = r"""<?
        $object->property;
        $object->foreach;
        $object->$variable;
        $object->$variable->schmariable;
        $object->$variable->$schmariable;
    ?>"""
    expected = [
        ObjectProperty(Variable('$object'), 'property'),
        ObjectProperty(Variable('$object'), 'foreach'),
        ObjectProperty(Variable('$object'), Variable('$variable')),
        ObjectProperty(ObjectProperty(Variable('$object'), Variable('$variable')),
                       'schmariable'),
        ObjectProperty(ObjectProperty(Variable('$object'), Variable('$variable')),
                       Variable('$schmariable')),
    ]
    eq_ast(input, expected)

def test_string_offset_lookups():
    input = r"""<?
        "$array[offset]";
        "$array[42]";
        "$array[$variable]";
        "${curly['offset']}";
        "$too[many][offsets]";
        "$next[to]$array";
        "$object->property";
        "$too->many->properties";
        "$adjacent->object$lookup";
        "$two->$variables";
        "stray -> [ ]";
        "not[array]";
        "non->object";
    ?>"""
    expected = [
        ArrayOffset(Variable('$array'), 'offset'),
        ArrayOffset(Variable('$array'), 42),
        ArrayOffset(Variable('$array'), Variable('$variable')),
        ArrayOffset(Variable('$curly'), 'offset'),
        BinaryOp('.', ArrayOffset(Variable('$too'), 'many'), '[offsets]'),
        BinaryOp('.', ArrayOffset(Variable('$next'), 'to'), Variable('$array')),
        ObjectProperty(Variable('$object'), 'property'),
        BinaryOp('.', ObjectProperty(Variable('$too'), 'many'), '->properties'),
        BinaryOp('.', ObjectProperty(Variable('$adjacent'), 'object'), Variable('$lookup')),
        BinaryOp('.', BinaryOp('.', Variable('$two'), '->'), Variable('$variables')),
        'stray -> [ ]',
        'not[array]',
        'non->object',
    ]
    eq_ast(input, expected)

def test_string_curly_dollar_expressions():
    input = r"""<?
        "a${dollar_curly}b";
        "c{$curly_dollar}d";
        "e${$dollar_curly_dollar}f";
        "{$array[0][1]}";
        "{$array['two'][3]}";
        "{$object->items[4]->five}";
        "{${$nasty}}";
        "{${funcall()}}";
        "{${$object->method()}}";
        "{$object->$variable}";
        "{$object->$variable[1]}";
        // "{${static_class::variable}}";
        // "{${static_class::$variable}}";
    ?>"""
    expected = [
        BinaryOp('.', BinaryOp('.', 'a', Variable('$dollar_curly')), 'b'),
        BinaryOp('.', BinaryOp('.', 'c', Variable('$curly_dollar')), 'd'),
        BinaryOp('.', BinaryOp('.', 'e', Variable('$dollar_curly_dollar')), 'f'),
        ArrayOffset(ArrayOffset(Variable('$array'), 0), 1),
        ArrayOffset(ArrayOffset(Variable('$array'), 'two'), 3),
        ObjectProperty(ArrayOffset(ObjectProperty(Variable('$object'), 'items'), 4), 'five'),
        Variable(Variable('$nasty')),
        Variable(FunctionCall('funcall', [])),
        Variable(MethodCall(Variable('$object'), 'method', [])),
        ObjectProperty(Variable('$object'), Variable('$variable')),
        ObjectProperty(Variable('$object'), ArrayOffset(Variable('$variable'), 1)),
        # StaticProperty('static_class', 'variable'),
        # StaticProperty('static_class', Variable('$variable')),
    ]
    eq_ast(input, expected)

def test_heredoc():
    input = r"""<?
        echo <<<EOT
This is a "$heredoc" with some $embedded->variables.
This is not the EOT; this is:
EOT;
    ?>"""
    expected = [
        Echo([BinaryOp('.',
                       BinaryOp('.',
                                BinaryOp('.',
                                         BinaryOp('.',
                                                  BinaryOp('.',
                                                           BinaryOp('.',
                                                                    BinaryOp('.',
                                                                             'This',
                                                                             ' is a "'),
                                                                    Variable('$heredoc')),
                                                           '" with some '),
                                                  ObjectProperty(Variable('$embedded'),
                                                                 'variables')),
                                         '.\n'),
                                'This'),
                       ' is not the EOT; this is:\n')]),
    ]
    eq_ast(input, expected)

def test_function_calls():
    input = r"""<?
        f();
        doit($arg1, &$arg2, 3 + 4);
    ?>"""
    expected = [
        FunctionCall('f', []),
        FunctionCall('doit',
                     [Parameter(Variable('$arg1'), False),
                      Parameter(Variable('$arg2'), True),
                      Parameter(BinaryOp('+', 3, 4), False)]),
    ]
    eq_ast(input, expected)                   

def test_method_calls():
    input = r"""<?
        $obj->meth($a, &$b, $c . $d);
        $chain->one($x)->two(&$y);
    ?>"""
    expected = [
        MethodCall(Variable('$obj'), 'meth',
                   [Parameter(Variable('$a'), False),
                    Parameter(Variable('$b'), True),
                    Parameter(BinaryOp('.', Variable('$c'), Variable('$d')), False)]),
        MethodCall(MethodCall(Variable('$chain'),
                              'one', [Parameter(Variable('$x'), False)]),
                   'two', [Parameter(Variable('$y'), True)]),
    ]
    eq_ast(input, expected)                   

def test_foreach():
    input = r"""<?
        foreach ($foo as $bar) {
            echo $bar;
        }
        foreach ($spam as $ham => $eggs) {
            echo "$ham: $eggs";
        }
        foreach (complex($expression) as &$ref)
            $ref++;
        foreach ($what as &$de => &$dealy):
            yo();
            yo();
        endforeach;
    ?>"""
    expected = [
        Foreach(Variable('$foo'), None, ForeachVariable('$bar', False),
                Block([Echo([Variable('$bar')])])),
        Foreach(Variable('$spam'),
                ForeachVariable('$ham', False),
                ForeachVariable('$eggs', False),
                Block([Echo([BinaryOp('.',
                                      BinaryOp('.', Variable('$ham'), ': '),
                                      Variable('$eggs'))])])),
        Foreach(FunctionCall('complex', [Parameter(Variable('$expression'),
                                                   False)]),
                None, ForeachVariable('$ref', True),
                PostIncDecOp('++', Variable('$ref'))),
        Foreach(Variable('$what'),
                ForeachVariable('$de', True),
                ForeachVariable('$dealy', True),
                Block([FunctionCall('yo', []),
                       FunctionCall('yo', [])])),
    ]
    eq_ast(input, expected)

def test_global_variables():
    input = r"""<?
        global $foo, $bar;
        global $$yo;
        global ${$dawg};
        global ${$obj->prop};
    ?>"""
    expected = [
        Global([Variable('$foo'), Variable('$bar')]),
        Global([Variable(Variable('$yo'))]),
        Global([Variable(Variable('$dawg'))]),
        Global([Variable(ObjectProperty(Variable('$obj'), 'prop'))]),
    ]
    eq_ast(input, expected)

def test_variable_variables():
    input = r"""<?
        $$a = $$b;
        $$a =& $$b;
        ${$a} = ${$b};
        ${$a} =& ${$b};
        $$a->b;
        $$$triple;
    ?>"""
    expected = [
        Assignment(Variable(Variable('$a')), Variable(Variable('$b')), False),
        Assignment(Variable(Variable('$a')), Variable(Variable('$b')), True),
        Assignment(Variable(Variable('$a')), Variable(Variable('$b')), False),
        Assignment(Variable(Variable('$a')), Variable(Variable('$b')), True),
        ObjectProperty(Variable(Variable('$a')), 'b'),
        Variable(Variable(Variable('$triple'))),
    ]
    eq_ast(input, expected)

def test_classes():
    input = r"""<?
        FINAL class Clown extends Unicycle implements RedNose, FacePaint {
            const the = 'only', constant = 'is';
            const change = 'chump';
            var $iable = 999, $nein;
            protected sTaTiC $x;
            public function conjunction_junction($arg1, $arg2) {
                return $arg1 . $arg2;
            }
        }
        class Stub {}
    ?>"""
    expected = [
        Class('Clown', 'final', 'Unicycle', ['RedNose', 'FacePaint'], [
            ClassConstants([ClassConstant('the', 'only'),
                            ClassConstant('constant', 'is')]),
            ClassConstants([ClassConstant('change', 'chump')]),
            ClassVariables([], [ClassVariable('$iable', 999),
                                ClassVariable('$nein', None)]),
            ClassVariables(['protected', 'static'],
                           [ClassVariable('$x', None)]),
            Method('conjunction_junction',
                   ['public'], 
                   [FormalParameter('$arg1', None, False),
                    FormalParameter('$arg2', None, False)],
                   [Return(BinaryOp('.', Variable('$arg1'), Variable('$arg2')))],
                   False),
        ]),
        Class('Stub', None, None, [], []),
    ]
    eq_ast(input, expected)

def test_new():
    input = r"""<?
        new Foo;
        new Foo();
        new Bar(1, 2, 3);
        $crusty =& new OldSyntax();
    ?>"""
    expected = [
        New('Foo', []),
        New('Foo', []),
        New('Bar', [Parameter(1, False),
                    Parameter(2, False),
                    Parameter(3, False)]),
        Assignment(Variable('$crusty'), New('OldSyntax', []), True),
    ]
    eq_ast(input, expected)

def test_exceptions():
    input = r"""<?
        try {
            $a = $b + $c;
            throw new Food($a);
        } catch (Food $f) {
            echo "Received food: $f";
        } catch (Exception $e) {
            echo "Problem?";
        }
    ?>"""
    expected = [
        Try([
            Assignment(Variable('$a'),
                       BinaryOp('+', Variable('$b'), Variable('$c')),
                       False),
            Throw(New('Food', [Parameter(Variable('$a'), False)])),
        ], [
            Catch('Food', Variable('$f'), [
                Echo([BinaryOp('.', 'Received food: ', Variable('$f'))])
            ]),
            Catch('Exception', Variable('$e'), [
                Echo(['Problem?']),
            ]),
        ])
    ]
    eq_ast(input, expected)

def test_declare():
    input = r"""<?
        declare(ticks=1) {
            echo 'hi';
        }
        declare(ticks=2);
        declare(ticks=3):
        echo 'bye';
        enddeclare;
    ?>"""
    expected = [
        Declare([Directive('ticks', 1)], Block([
            Echo(['hi']),
        ])),
        Declare([Directive('ticks', 2)], None),
        Declare([Directive('ticks', 3)], Block([
            Echo(['bye']),
        ])),
    ]
    eq_ast(input, expected)

def test_instanceof():
    input = r"""<?
        if ($foo iNsTaNcEoF Bar) {
            echo '$foo is a bar';
        }
        $foo instanceof $bar;
    ?>"""
    expected = [
        If(BinaryOp('instanceof', Variable('$foo'), Constant('Bar')),
           Block([Echo(['$foo is a bar'])]), [], None),
        BinaryOp('instanceof', Variable('$foo'), Variable('$bar')),
    ]
    eq_ast(input, expected)
