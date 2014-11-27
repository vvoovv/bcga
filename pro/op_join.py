from .base import ComplexOperator, context, countOperator

def join(neighbor, *args):
    return context.factory["Join"](neighbor, *args)

class Join(ComplexOperator):
    def __init__(self, neighbor, *args):
        self.neighbor = neighbor
        self.args = args
        # count operators
        numOperators = 0
        for arg in args:
            if countOperator(arg):
                numOperators += 1
        super().__init__(numOperators)
