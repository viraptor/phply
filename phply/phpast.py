# ----------------------------------------------------------------------
# phpast.py
#
# PHP abstract syntax node definitions.
# ----------------------------------------------------------------------

class Node(object):
    fields = []

    def __init__(self, *args, **kwargs):
        assert len(self.fields) == len(args), \
            '%s takes %d arguments' % (self.__class__.__name__,
                                       len(self.fields))
        try:
            self.lineno = kwargs['lineno']
        except KeyError:
            self.lineno = None
        for i, field in enumerate(self.fields):
            setattr(self, field, args[i])

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__,
                           ', '.join([repr(getattr(self, field))
                                      for field in self.fields]))

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        for field in self.fields:
            if not (getattr(self, field) == getattr(other, field)):
                return False
        return True

    def accept(self, visitor):
        visitor(self)
        for field in self.fields:
            value = getattr(self, field)
            if isinstance(value, Node):
                value.accept(visitor)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, Node):
                        item.accept(visitor)

    def generic(self, with_lineno=False):
        values = {}
        if with_lineno:
            values['lineno'] = self.lineno
        for field in self.fields:
            value = getattr(self, field)
            if hasattr(value, 'generic'):
                value = value.generic(with_lineno)
            elif isinstance(value, list):
                items = value
                value = []
                for item in items:
                    if hasattr(item, 'generic'):
                        item = item.generic(with_lineno)
                    value.append(item)
            values[field] = value
        return (self.__class__.__name__, values)

def node(name, fields):
    attrs = {'fields': fields}
    return type(name, (Node,), attrs)

InlineHTML = node('InlineHTML', ['data'])
Block = node('Block', ['nodes'])
Assignment = node('Assignment', ['node', 'expr', 'is_ref'])
ListAssignment = node('ListAssignment', ['nodes', 'expr'])
New = node('New', ['name', 'params'])
Clone = node('Clone', ['node'])
Break = node('Break', ['node'])
Continue = node('Continue', ['node'])
Return = node('Return', ['node'])
Yield = node('Yield', ['node'])
Global = node('Global', ['nodes'])
Static = node('Static', ['nodes'])
Echo = node('Echo', ['nodes'])
Print = node('Print', ['node'])
Unset = node('Unset', ['nodes'])
Try = node('Try', ['nodes', 'catches', 'finally'])
Catch = node('Catch', ['class_', 'var', 'nodes'])
Finally = node('Finally', ['nodes'])
Throw = node('Throw', ['node'])
Declare = node('Declare', ['directives', 'node'])
Directive = node('Directive', ['name', 'node'])
Function = node('Function', ['name', 'params', 'nodes', 'is_ref'])
Method = node('Method', ['name', 'modifiers', 'params', 'nodes', 'is_ref'])
Closure = node('Closure', ['params', 'vars', 'nodes', 'is_ref'])
Class = node('Class', ['name', 'type', 'extends', 'implements', 'traits', 'nodes'])
Trait = node('Trait', ['name', 'traits', 'nodes'])
ClassConstants = node('ClassConstants', ['nodes'])
ClassConstant = node('ClassConstant', ['name', 'initial'])
ClassVariables = node('ClassVariables', ['modifiers', 'nodes'])
ClassVariable = node('ClassVariable', ['name', 'initial'])
Interface = node('Interface', ['name', 'extends', 'nodes'])
AssignOp = node('AssignOp', ['op', 'left', 'right'])
BinaryOp = node('BinaryOp', ['op', 'left', 'right'])
UnaryOp = node('UnaryOp', ['op', 'expr'])
TernaryOp = node('TernaryOp', ['expr', 'iftrue', 'iffalse'])
PreIncDecOp = node('PreIncDecOp', ['op', 'expr'])
PostIncDecOp = node('PostIncDecOp', ['op', 'expr'])
Cast = node('Cast', ['type', 'expr'])
IsSet = node('IsSet', ['nodes'])
Empty = node('Empty', ['expr'])
Eval = node('Eval', ['expr'])
Include = node('Include', ['expr', 'once'])
Require = node('Require', ['expr', 'once'])
Exit = node('Exit', ['expr', 'type'])
Silence = node('Silence', ['expr'])
MagicConstant = node('MagicConstant', ['name', 'value'])
Constant = node('Constant', ['name'])
Variable = node('Variable', ['name'])
StaticVariable = node('StaticVariable', ['name', 'initial'])
LexicalVariable = node('LexicalVariable', ['name', 'is_ref'])
FormalParameter = node('FormalParameter', ['name', 'default', 'is_ref', 'type'])
Parameter = node('Parameter', ['node', 'is_ref'])
FunctionCall = node('FunctionCall', ['name', 'params'])
Array = node('Array', ['nodes'])
ArrayElement = node('ArrayElement', ['key', 'value', 'is_ref'])
ArrayOffset = node('ArrayOffset', ['node', 'expr'])
StringOffset = node('StringOffset', ['node', 'expr'])
ObjectProperty = node('ObjectProperty', ['node', 'name'])
StaticProperty = node('StaticProperty', ['node', 'name'])
MethodCall = node('MethodCall', ['node', 'name', 'params'])
StaticMethodCall = node('StaticMethodCall', ['class_', 'name', 'params'])
If = node('If', ['expr', 'node', 'elseifs', 'else_'])
ElseIf = node('ElseIf', ['expr', 'node'])
Else = node('Else', ['node'])
While = node('While', ['expr', 'node'])
DoWhile = node('DoWhile', ['node', 'expr'])
For = node('For', ['start', 'test', 'count', 'node'])
Foreach = node('Foreach', ['expr', 'keyvar', 'valvar', 'node'])
ForeachVariable = node('ForeachVariable', ['name', 'is_ref'])
Switch = node('Switch', ['expr', 'nodes'])
Case = node('Case', ['expr', 'nodes'])
Default = node('Default', ['nodes'])
Namespace = node('Namespace', ['name', 'nodes'])
UseDeclarations = node('UseDeclarations', ['nodes'])
UseDeclaration = node('UseDeclaration', ['name', 'alias'])
ConstantDeclarations = node('ConstantDeclarations', ['nodes'])
ConstantDeclaration = node('ConstantDeclaration', ['name', 'initial'])
TraitUse = node('TraitUse', ['name', 'renames'])
TraitModifier = node('TraitModifier', ['from', 'to', 'visibility'])

def resolve_magic_constants(nodes):
    current = {}
    def visitor(node):
        if isinstance(node, Namespace):
            current['namespace'] = node.name
        elif isinstance(node, Class):
            current['class'] = node.name
        elif isinstance(node, Function):
            current['function'] = node.name
        elif isinstance(node, Method):
            current['method'] = node.name
        elif isinstance(node, MagicConstant):
            if node.name == '__NAMESPACE__':
                node.value = current.get('namespace')
            elif node.name == '__CLASS__':
                node.value = current.get('class')
                if current.get('namespace'):
                    node.value = '%s\\%s' % (current.get('namespace'),
                                             node.value)
            elif node.name == '__FUNCTION__':
                node.value = current.get('function')
                if current.get('namespace'):
                    node.value = '%s\\%s' % (current.get('namespace'),
                                             node.value)
            elif node.name == '__METHOD__':
                node.value = current.get('method')
                if current.get('class'):
                    node.value = '%s::%s' % (current.get('class'),
                                             node.value)
                if current.get('namespace'):
                    node.value = '%s\\%s' % (current.get('namespace'),
                                             node.value)
    for node in nodes:
        if isinstance(node, Node):
            node.accept(visitor)
