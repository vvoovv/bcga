from .base import Operator, ComplexOperator, context

def inset(*args, **kwargs):
    return context.factory["Inset"](*args, **kwargs)

class Inset(ComplexOperator):
    def __init__(self, *args, **kwargs):
        self.height = kwargs["height"] if "height" in kwargs else None
        self.cap = None
        self.side = None
        numOperators = 0
        # a list with definitions of insets
        insets = []
        for arg in args:
            if isinstance(arg, Operator):
                if isinstance(arg.value, str):
                    # rule or operator
                    setattr(self, arg.value, arg)
                else:
                    # inset definition
                    insets.append(arg)
                if arg.count:
                    arg.count = False
                    numOperators += 1
            else:
                # inset definition
                insets.append(arg)
        self.insets = insets
        super().__init__(numOperators)