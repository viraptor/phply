from __future__ import print_function

from phply import phplex
from phply.phpparse import make_parser
from phply.phpast import *

import nose.tools
import pprint

parser = make_parser()

def eq_ast(input, expected, filename=None, with_top_lineno=False):
    lexer = phplex.lexer.clone()
    lexer.filename = filename
    output = parser.parse(input, lexer=lexer)
    resolve_magic_constants(output)

    print('Parser output:')
    pprint.pprint(output)
    print()

    print('Node by node:')
    for out, exp in zip(output, expected):
        print('\tgot:', out, '\texpected:', exp)
        nose.tools.eq_(out, exp)

        # compare line numbers, but only for top elements
        if with_top_lineno:
            print('\tgot line:', out.lineno, '\texpected:', exp.lineno)
            nose.tools.eq_(out.lineno, exp.lineno)

    assert len(output) == len(expected), \
           'output length was %d, expected %s' % (len(output), len(expected))

def test_inline_html():
    input = 'html <?php // php ?> more html'
    expected = [InlineHTML('html '), InlineHTML(' more html')]
    eq_ast(input, expected)

def test_echo():
    input = '<?php echo "hello, world!"; ?>'
    expected = [Echo(["hello, world!"])]
    eq_ast(input, expected)

def test_open_tag_with_echo():
    input = '<?= "hello, world!" ?><?= "test"; EXTRA; ?>'
    expected = [
        Echo(["hello, world!"]),
        Echo(["test"]),
        Constant('EXTRA'),
    ]
    eq_ast(input, expected)

def test_exit():
    input = '<?php exit; exit(); exit(123); die; die(); die(456); ?>'
    expected = [
        Exit(None, 'exit'), Exit(None, 'exit'), Exit(123, 'exit'),
        Exit(None, 'die'), Exit(None, 'die'), Exit(456, 'die'),
    ]
    eq_ast(input, expected)

def test_isset():
    input = r"""<?php
        isset($a);
        isset($b->c);
        isset($d['e']);
        isset($f, $g);
        isset($h->m()['i1']['i2']);
    ?>"""
    expected = [
        IsSet([Variable('$a')]),
        IsSet([ObjectProperty(Variable('$b'), 'c')]),
        IsSet([ArrayOffset(Variable('$d'), 'e')]),
        IsSet([Variable('$f'), Variable('$g')]),
        IsSet([ArrayOffset(ArrayOffset(MethodCall(Variable('$h'), 'm', []), 'i1'), 'i2')]),
    ]
    eq_ast(input, expected)

def test_namespace_names():
    input = r"""<?php
        foo;
        bar\baz;
        one\too\tree;
        \top;
        \top\level;
        namespace\level;
    ?>"""
    expected = [
        Constant(r'foo'),
        Constant(r'bar\baz'),
        Constant(r'one\too\tree'),
        Constant(r'\top'),
        Constant(r'\top\level'),
        Constant(r'namespace\level'),
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

def test_string_unescape():
    input = r"""<?
        '\r\n\t\\\'';
        "\r\n\t\\\"";
    ?>"""
    # TODO: "\x97\x[0-9]";
    expected = [
        r"\r\n\t\'",
        "\r\n\t\\\"",
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
        "{${static_class::constant}}";
        "{${static_class::$variable}}";
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
        Variable(StaticProperty('static_class', 'constant')),
        Variable(StaticProperty('static_class', Variable('$variable'))),
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
                       ' is not the EOT; this is:')]),
    ]
    eq_ast(input, expected)

def test_function_calls():
    input = r"""<?
        f();
        doit($arg1, &$arg2, 3 + 4);
        name\spaced();
        \name\spaced();
        namespace\d();
    ?>"""
    expected = [
        FunctionCall('f', []),
        FunctionCall('doit',
                     [Parameter(Variable('$arg1'), False),
                      Parameter(Variable('$arg2'), True),
                      Parameter(BinaryOp('+', 3, 4), False)]),
        FunctionCall('name\\spaced', []),
        FunctionCall('\\name\\spaced', []),
        FunctionCall('namespace\\d', []),
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

def test_if():
    input = r"""<?
        if (1)
            if (2)
                echo 3;
            else
                echo 4;
        else
            echo 5;
        if ($a < $b) {
            return -1;
        } elseif ($a > $b) {
            return 1;
        } elseif ($a == $b) {
            return 0;
        } else {
            return 'firetruck';
        }
        if ($if):
            echo 'a';
        elseif ($elseif):
            echo 'b';
        else:
            echo 'c';
        endif;
    ?>"""
    expected = [
        If(1,
           If(2,
              Echo([3]),
              [],
              Else(Echo([4]))),
           [],
           Else(Echo([5]))),
        If(BinaryOp('<', Variable('$a'), Variable('$b')),
           Block([Return(UnaryOp('-', 1))]),
           [ElseIf(BinaryOp('>', Variable('$a'), Variable('$b')),
                   Block([Return(1)])),
            ElseIf(BinaryOp('==', Variable('$a'), Variable('$b')),
                   Block([Return(0)]))],
           Else(Block([Return('firetruck')]))),
        If(Variable('$if'),
           Block([Echo(['a'])]),
           [ElseIf(Variable('$elseif'),
                   Block([Echo(['b'])]))],
           Else(Block([Echo(['c'])]))),
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
        foreach ($what as $de => &$dealy):
            yo();
            yo();
        endforeach;
        foreach ($foo as $bar[0]) {}
    ?>"""
    expected = [
        Foreach(Variable('$foo'), None, ForeachVariable(Variable('$bar'), False),
                Block([Echo([Variable('$bar')])])),
        Foreach(Variable('$spam'),
                Variable('$ham'),
                ForeachVariable(Variable('$eggs'), False),
                Block([Echo([BinaryOp('.',
                                      BinaryOp('.', Variable('$ham'), ': '),
                                      Variable('$eggs'))])])),
        Foreach(FunctionCall('complex', [Parameter(Variable('$expression'),
                                                   False)]),
                None, ForeachVariable(Variable('$ref'), True),
                PostIncDecOp('++', Variable('$ref'))),
        Foreach(Variable('$what'),
                Variable('$de'),
                ForeachVariable(Variable('$dealy'), True),
                Block([FunctionCall('yo', []),
                       FunctionCall('yo', [])])),
        Foreach(Variable('$foo'),
                None,
                ForeachVariable(ArrayOffset(Variable('$bar'), 0), False),
                Block([])),
    ]
    eq_ast(input, expected)

def test_foreach_with_lists():
    input = r"""<?
        foreach ($foo as list($bar, $baz)) {}
        foreach ($foo as $k => list($bar, $baz)) {}
    ?>"""
    expected = [
        Foreach(Variable('$foo'), None, ForeachVariable([Variable('$bar'), Variable('$baz')], False), Block([])),
        Foreach(Variable('$foo'), Variable('$k'), ForeachVariable([Variable('$bar'), Variable('$baz')], False), Block([])),
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
        Class('Clown', 'final', 'Unicycle', ['RedNose', 'FacePaint'], [], [
            ClassConstants([ClassConstant('the', 'only'),
                            ClassConstant('constant', 'is')]),
            ClassConstants([ClassConstant('change', 'chump')]),
            ClassVariables([], [ClassVariable('$iable', 999),
                                ClassVariable('$nein', None)]),
            ClassVariables(['protected', 'static'],
                           [ClassVariable('$x', None)]),
            Method('conjunction_junction',
                   ['public'], 
                   [FormalParameter('$arg1', None, False, None),
                    FormalParameter('$arg2', None, False, None)],
                   [Return(BinaryOp('.', Variable('$arg1'), Variable('$arg2')))],
                   False),
        ]),
        Class('Stub', None, None, [], [], []),
    ]
    eq_ast(input, expected)

def test_new():
    input = r"""<?
        new Foo;
        new Foo();
        new Bar(1, 2, 3);
        $crusty =& new OldSyntax();
        new name\Spaced();
        new \name\Spaced();
        new namespace\D();
    ?>"""
    expected = [
        New('Foo', []),
        New('Foo', []),
        New('Bar', [Parameter(1, False),
                    Parameter(2, False),
                    Parameter(3, False)]),
        Assignment(Variable('$crusty'), New('OldSyntax', []), True),
        New('name\\Spaced', []),
        New('\\name\\Spaced', []),
        New('namespace\\D', []),
    ]
    eq_ast(input, expected)

def test_exceptions():
    input = r"""<?
        try {
            $a = $b + $c;
            throw new Food($a);
        } catch (Food $f) {
            echo "Received food: $f";
        } catch (\Bar\Food $f) {
            echo "Received bar food: $f";
        } catch (namespace\Food $f) {
            echo "Received namespace food: $f";
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
            Catch('\\Bar\\Food', Variable('$f'), [
                Echo([BinaryOp('.', 'Received bar food: ', Variable('$f'))])
            ]),
            Catch('namespace\\Food', Variable('$f'), [
                Echo([BinaryOp('.', 'Received namespace food: ', Variable('$f'))])
            ]),
            Catch('Exception', Variable('$e'), [
                Echo(['Problem?']),
            ]),
        ],
        None)
    ]
    eq_ast(input, expected)

def test_catch_finally():
    input = r"""<?
        try {
            1;
        } catch (Exception $e) {
            2;
        } finally {
            3;
        }
    ?>"""
    expected = [
        Try([
            1
        ], [
            Catch('Exception', Variable('$e'), [
                2
            ]),
        ],
        Finally([3]))
    ]
    eq_ast(input, expected)

def test_just_finally():
    input = r"""<?
        try {
        } finally {
            1;
        }
    ?>"""
    expected = [
        Try([
        ], [],
        Finally([1]))
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
        $foo instanceof static;
    ?>"""
    expected = [
        If(BinaryOp('instanceof', Variable('$foo'), Constant('Bar')),
           Block([Echo(['$foo is a bar'])]), [], None),
        BinaryOp('instanceof', Variable('$foo'), Variable('$bar')),
        BinaryOp('instanceof', Variable('$foo'), 'static'),
    ]
    eq_ast(input, expected)

def test_static_members():
    input = r"""<?
        Ztatic::constant;
        Ztatic::$variable;
        Ztatic::method();
        Ztatic::$variable_method();
        static::late_binding;
        STATIC::$late_binding;
        Static::late_binding();
    ?>"""
    expected = [
        StaticProperty('Ztatic', 'constant'),
        StaticProperty('Ztatic', Variable('$variable')),
        StaticMethodCall('Ztatic', 'method', []),
        StaticMethodCall('Ztatic', Variable('$variable_method'), []),
        StaticProperty('static', 'late_binding'),
        StaticProperty('static', Variable('$late_binding')),
        StaticMethodCall('static', 'late_binding', []),
    ]
    eq_ast(input, expected)

def test_casts():
    input = r"""<?
        (aRray) $x;
        (bOol) $x;
        (bOolean) $x;
        (rEal) $x;
        (dOuble) $x;
        (fLoat) $x;
        (iNt) $x;
        (iNteger) $x;
        (sTring) $x;
        (uNset) $x;
        (bInary) $x;
    ?>"""
    expected = [
        Cast('array', Variable('$x')),
        Cast('bool', Variable('$x')),
        Cast('bool', Variable('$x')),
        Cast('double', Variable('$x')),
        Cast('double', Variable('$x')),
        Cast('double', Variable('$x')),
        Cast('int', Variable('$x')),
        Cast('int', Variable('$x')),
        Cast('string', Variable('$x')),
        Cast('unset', Variable('$x')),
        Cast('binary', Variable('$x')),
    ]
    eq_ast(input, expected)

def test_namespaces():
    input = r"""<?
        namespace my\name;
        namespace my\name {
            foo();
            bar();
        }
        namespace {
            foo();
            bar();
        }
    ?>"""
    expected = [
        Namespace('my\\name', []),
        Namespace('my\\name', [FunctionCall('foo', []),
                               FunctionCall('bar', [])]),
        Namespace(None, [FunctionCall('foo', []),
                         FunctionCall('bar', [])]),
    ]
    eq_ast(input, expected)

def test_use_declarations():
    input = r"""<?
        use me;
        use \me;
        use \me\please;
        use my\name as foo;
        use a, b;
        use a as b, \c\d\e as f;
    ?>"""
    expected = [
        UseDeclarations([UseDeclaration('me', None)]),
        UseDeclarations([UseDeclaration('\\me', None)]),
        UseDeclarations([UseDeclaration('\\me\\please', None)]),
        UseDeclarations([UseDeclaration('my\\name', 'foo')]),
        UseDeclarations([UseDeclaration('a', None),
                         UseDeclaration('b', None)]),
        UseDeclarations([UseDeclaration('a', 'b'),
                         UseDeclaration('\\c\\d\\e', 'f')]),
    ]
    eq_ast(input, expected)

def test_constant_declarations():
    input = r"""<?
        const foo = 42;
        const bar = 'baz', wat = \DOO;
        const ant = namespace\level;
        const dq1 = "";
        const dq2 = "nothing fancy";
    ?>"""
    expected = [
        ConstantDeclarations([ConstantDeclaration('foo', 42)]),
        ConstantDeclarations([ConstantDeclaration('bar', 'baz'),
                              ConstantDeclaration('wat', Constant('\\DOO'))]),
        ConstantDeclarations([ConstantDeclaration('ant', Constant('namespace\\level'))]),
        ConstantDeclarations([ConstantDeclaration('dq1', '')]),
        ConstantDeclarations([ConstantDeclaration('dq2', 'nothing fancy')]),
    ]
    eq_ast(input, expected)

def test_closures():
    input = r"""<?
        $greet = function($name) {
            printf("Hello %s\r\n", $name);
        };
        $greet('World');
        $cb = function&($a, &$b) use ($c, &$d) {};
    ?>"""
    expected = [
        Assignment(Variable('$greet'),
                   Closure([FormalParameter('$name', None, False, None)],
                           [],
                           [FunctionCall('printf',
                                         [Parameter('Hello %s\r\n', False),
                                          Parameter(Variable('$name'), False)])],
                           False),
                   False),
        FunctionCall(Variable('$greet'), [Parameter('World', False)]),
        Assignment(Variable('$cb'),
                   Closure([FormalParameter('$a', None, False, None),
                            FormalParameter('$b', None, True, None)],
                           [LexicalVariable('$c', False),
                            LexicalVariable('$d', True)],
                           [],
                           True),
                   False),
    ]
    eq_ast(input, expected)

def test_magic_constants():
    input = r"""<?
        namespace Shmamespace;

        function p($x) {
            echo __FUNCTION__ . ': ' . $x . "\n";
        }

        class Bar {
            function __construct() {
                p(__LINE__);
                p(__DIR__);
                p(__FILE__);
                p(__NAMESPACE__);
                p(__CLASS__);
                p(__METHOD__);
            }
        }

        new Bar();
    ?>"""
    expected = [
        Namespace('Shmamespace', []),
        Function('p', [FormalParameter('$x', None, False, None)], [
            Echo([BinaryOp('.', BinaryOp('.', BinaryOp('.',
                MagicConstant('__FUNCTION__', 'Shmamespace\\p'), ': '),
                Variable('$x')), '\n')])
        ], False),
        Class('Bar', None, None, [], [],
              [Method('__construct', [], [],
                      [FunctionCall('p', [Parameter(MagicConstant('__LINE__', 10), False)]),
                       FunctionCall('p', [Parameter(MagicConstant('__DIR__', '/my/dir'), False)]),
                       FunctionCall('p', [Parameter(MagicConstant('__FILE__', '/my/dir/file.php'), False)]),
                       FunctionCall('p', [Parameter(MagicConstant('__NAMESPACE__', 'Shmamespace'), False)]),
                       FunctionCall('p', [Parameter(MagicConstant('__CLASS__', 'Shmamespace\\Bar'), False)]),
                       FunctionCall('p', [Parameter(MagicConstant('__METHOD__', 'Shmamespace\\Bar::__construct'), False)])], False)]),
        New('Bar', []),
    ]
    eq_ast(input, expected, filename='/my/dir/file.php')

def test_type_hinting():
    input = r"""<?
    function foo(Foo $var1, Bar $var2=1, Quux &$var3, Corge &$var4=1, array &$var5=array()) {
    }
    ?>""";
    expected = [
        Function('foo', 
            [FormalParameter('$var1', None, False, 'Foo'),
             FormalParameter('$var2', 1, False, 'Bar'),
             FormalParameter('$var3', None, True, 'Quux'),
             FormalParameter('$var4', 1, True, 'Corge'),
             FormalParameter('$var5', Array([]), True, 'array')],
            [],
            False)]
    eq_ast(input, expected)

def test_static_scalar_class_constants():
    input = r"""<?
    class A { public $b = self::C; function d($var1=self::C) {} }
    ?>"""
    expected = [
        Class('A', None, None, [], [],
            [ClassVariables(['public'], [ClassVariable('$b', StaticProperty('self', 'C'))]),
             Method('d', [], [FormalParameter('$var1', StaticProperty('self', 'C'), False, None)], [], False)
            ])]
    eq_ast(input, expected)

def test_backtick_shell_exec():
    input = '<? `$cmd` . `date`; `echo $line`; ?>'
    expected = [
        BinaryOp('.',
            FunctionCall('shell_exec', [Parameter(Variable('$cmd'), False)]),
            FunctionCall('shell_exec', [Parameter('date', False)])
        ),
        FunctionCall('shell_exec', [Parameter(BinaryOp('.', 'echo ', Variable('$line')), False)])
    ]
    eq_ast(input, expected)

def test_open_close_tags_ignore():
    # The filtered lexer should correctly interpret ?><?
    input = '<? if (1): if (2) 3; ?><? else: 0; endif;'
    expected = [
        If(1, Block([If(2, 3, [], None), None]), [], Else(Block([0])))
    ]
    eq_ast(input, expected)

def test_ternary():
    input = '<? 1 ? 2 : 3; 4 ? : 5;'
    expected = [
        TernaryOp(1, 2, 3),
        TernaryOp(4, 4, 5),
    ]
    eq_ast(input, expected)

def test_array_dereferencing():
    input = '<? $a->method()[0]; func()[1];'
    expected = [
        ArrayOffset(MethodCall(Variable('$a'), 'method', []), 0),
        ArrayOffset(FunctionCall('func', []), 1)
    ]
    eq_ast(input, expected)

def test_array_literal():
    input = '<? [1,2]; [];'
    expected = [
        Array([ArrayElement(None, 1, False), ArrayElement(None, 2, False)]),
        Array([]),
    ]
    eq_ast(input, expected)

def test_array_in_default_arg():
    input = '<? function f($a=[]){} function g($a=array()){}'
    expected = [
        Function('f', [FormalParameter('$a', Array([]), False, None)], [], False),
        Function('g', [FormalParameter('$a', Array([]), False, None)], [], False),
    ]
    eq_ast(input, expected)

def test_const_heredoc():
    input = '''<?
    const X = <<<HERE
text
HERE;'''
    expected = [
        ConstantDeclarations([ConstantDeclaration('X', 'text')])
    ]
    eq_ast(input, expected)

def test_object_property_on_expr():
    input = '''<? ($a->m1())->m2(); ($a->m1())->m2;'''
    expected = [
        MethodCall(MethodCall(Variable('$a'), 'm1', []), 'm2', []),
        ObjectProperty(MethodCall(Variable('$a'), 'm1', []), 'm2'),
    ]
    eq_ast(input, expected)

def test_binary_string():
    input = '''<? b"abc"; b'abc';'''
    expected = [
        "abc",
        "abc",
    ]
    eq_ast(input, expected)

def test_class_trait_use():
    input = '''<? class A { use B; }'''
    expected = [
        Class('A', None, None, [], [TraitUse('B', [])], []),
    ]
    eq_ast(input, expected)

def test_trait():
    input = '''<? trait A { } trait B { use A; } trait C { function f(){} }
                  trait D { protected $v; }'''
    expected = [
        Trait('A', [], []),
        Trait('B', [TraitUse('A', [])], []),
        Trait('C', [], [Method('f', [], [], [], False)]),
        Trait('D', [], [ClassVariables(['protected'], [ClassVariable('$v', None)])]),
    ]
    eq_ast(input, expected)

def test_trait_renames():
    input = '''<? trait A { use T {X as Y;} }
                  class B { use T {X as Y;} }
                  trait C { use T {X as public Y;} }
                  trait D { use T {X as public;} }
                  trait E { use T {X::m as Y;} }'''
    expected = [
        Trait('A', [TraitUse('T', [TraitModifier('X', 'Y', None)])], []),
        Class('B', None, None, [], [TraitUse('T', [TraitModifier('X', 'Y', None)])], []),
        Trait('C', [TraitUse('T', [TraitModifier('X', 'Y', 'public')])], []),
        Trait('D', [TraitUse('T', [TraitModifier('X', None, 'public')])], []),
        Trait('E', [TraitUse('T', [TraitModifier(StaticProperty('X', 'm'), 'Y', None)])], []),
    ]
    eq_ast(input, expected)

def test_class_name_as_string():
    input = '''<? A::class; const C = A::class;'''
    expected = [
        'A',
        ConstantDeclarations([ConstantDeclaration('C', 'A')]),
    ]
    eq_ast(input, expected)

def test_static_expressions():
    input = '''<? const C = 1+2; const C = 1+(2+3); const C = "a"."b";'''
    expected = [
        ConstantDeclarations([ConstantDeclaration('C', BinaryOp('+', 1, 2))]),
        ConstantDeclarations([ConstantDeclaration('C', BinaryOp('+', 1, BinaryOp('+', 2, 3)))]),
        ConstantDeclarations([ConstantDeclaration('C', BinaryOp('.', 'a', 'b'))]),
    ]
    eq_ast(input, expected)

def test_const_arrays():
    input = '''<? const C = array(1+2);'''
    expected = [
        ConstantDeclarations([ConstantDeclaration('C', Array([ArrayElement(None, BinaryOp('+', 1, 2), False)]))]),
    ]
    eq_ast(input, expected)

def test_numbers():
    input = '''<? 10; 010; 0x10; 0b10;'''
    expected = [
        10,
        0o10,
        0x10,
        2,
    ]
    eq_ast(input, expected)

def test_result_multiple_offsets():
    input = '''<? $o->m()[1][2]; $o->m(){1}{2}; '''
    expected = [
        ArrayOffset(ArrayOffset(MethodCall(Variable('$o'), 'm', []), 1), 2),
        StringOffset(StringOffset(MethodCall(Variable('$o'), 'm', []), 1), 2),
    ]
    eq_ast(input, expected)

def test_yield():
    input = '''<? function f() { yield; yield 1; }'''
    expected = [
        Function('f', [], [
            Yield(None),
            Yield(1),
        ], False),
    ]
    eq_ast(input, expected)

def test_static_property_dynamic_access():
    input = '''<? $o::{$prop};'''
    expected = [
        StaticProperty(Variable('$o'), Variable('$prop')),
    ]
    eq_ast(input, expected)

def test_static_property_dynamic_call():
    input = '''<? $o::{$prop}();'''
    expected = [
        StaticMethodCall(Variable('$o'), Variable('$prop'), []),
    ]
    eq_ast(input, expected)

def test_nowdoc():
    input = r"""<?
        echo <<<'EOT'
disregard $all {$crazy} ${stuff}->f();
and `this`
EOT;
    ?>"""
    expected = [
        Echo(['disregard $all {$crazy} ${stuff}->f();\nand `this`'])
    ]
    eq_ast(input, expected)

def test_exit_loc():
    input = '''<?
               exit(1); '''
    expected = [
        Exit(1, 'exit', lineno=2)
    ]
    eq_ast(input, expected, with_top_lineno=True)
