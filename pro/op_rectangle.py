from .base import ComplexOperator, context, countOperator

def rectangle(xSize, ySize, operator=None, **kwargs):
    """
    Creates a rectangle with sides along local x and y axis of the current shape
    """
    return context.factory["Rectangle"](xSize, ySize, operator, **kwargs)

class Rectangle(ComplexOperator):
    def __init__(self, xSize, ySize, operator, **kwargs):
        self.xSize = xSize
        self.ySize = ySize
        self.operator = operator
        
        self.replace = False
        # apply kwargs
        for k in kwargs:
            setattr(self, k, kwargs[k])
        
        numOperators = 1 if countOperator(operator) else 0
        super().__init__(numOperators)