from .base import ComplexOperator, context

def copy(operator=None, **kwargs):
    return context.factory["Copy"](operator, **kwargs)

class Copy(ComplexOperator):
    def __init__(self, operator, **kwargs):
        if operator:
            self.operator = operator
            operator.count = False
            numOperators = 1
        else:
            self.operator = None
            numOperators = 0
        
        super().__init__(numOperators)