from .base import Operator, ComplexOperator, context
from .base import Modifier

def inset2(*args, **kwargs):
    return context.factory["Inset2"](*args, **kwargs)

class Inset2(ComplexOperator):
    def __init__(self, *args, **kwargs):
        self.cap = None
        self.side = None
        # which edges to exclude?
        self.exclude = None
        self.keepOriginal = False
        numOperators = 0
        # a list with definitions of insets
        insets = []
        numArgs = len(args)
        i = 0
        while i<numArgs:
            arg = args[i]
            if isinstance(arg, Operator):
                # rule or operator
                setattr(self, arg.value, arg)
                if arg.count:
                    arg.count = False
                    numOperators += 1
            elif isinstance(arg, Modifier):
                # TODO: the special function like arc()
                insets.append(arg)
            else:
                # inset definition
                insets.append((arg, args[i+1]))
                # check if we've got an operator for args[i+1]
                i += 1
                arg = args[i]
                if isinstance(arg, Operator):
                    if arg.count:
                        arg.count = False
                        numOperators += 1
            i += 1
        self.insets = insets
        super().__init__(numOperators)