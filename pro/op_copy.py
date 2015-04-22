from .base import ComplexOperator, context, countOperator

def copy(operator=None, **kwargs):
    return context.factory["Copy"](operator, **kwargs)

class Copy(ComplexOperator):
    def __init__(self, operator, **kwargs):
        self.operator = operator
        numOperators = 1 if countOperator(operator) else 0
        super().__init__(numOperators)