# ----------------------------------------------------------------------
# phpast.py
#
# PHP abstract syntax node definitions.
# ----------------------------------------------------------------------

class Node(object):
    fields = []

    def __init__(self, *args, **kwargs):
        assert len(self.fields) == len(args)
        try:
            self.lineno = kwargs['lineno']
        except KeyError:
            self.lineno = None
        for i, field in enumerate(self.fields):
            setattr(self, field, args[i])

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__,
                           [getattr(self, field) for field in self.fields])

    def generic(self):
        values = {}
        for field in self.fields:
            value = getattr(self, field)
            if hasattr(value, 'generic'):
                value = value.generic()
            elif isinstance(value, list):
                items = value
                value = []
                for item in items:
                    if hasattr(item, 'generic'):
                        item = item.generic()
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
Break = node('Break', ['node'])
Continue = node('Continue', ['node'])
Return = node('Return', ['node'])
Global = node('Global', ['nodes'])
Static = node('Static', ['nodes'])
Echo = node('Echo', ['nodes'])
Unset = node('Unset', ['nodes'])
Function = node('Function', ['params', 'nodes', 'is_ref'])
BinaryOp = node('BinaryOp', ['op', 'left', 'right'])
UnaryOp = node('UnaryOp', ['op', 'expr'])
Constant = node('Constant', ['name'])
Variable = node('Variable', ['name'])
StaticVariable = node('StaticVariable', ['name', 'initial'])
FormalParameter = node('FormalParameter', ['name', 'default', 'is_ref'])
Parameter = node('Parameter', ['node', 'is_ref'])
FunctionCall = node('FunctionCall', ['name', 'params'])
Array = node('Array', ['nodes'])
ArrayElement = node('ArrayElement', ['name', 'node', 'is_ref'])
ArrayOffset = node('ArrayOffset', ['node', 'expr'])
StringOffset = node('StringOffset', ['node', 'expr'])
