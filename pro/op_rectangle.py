from .base import Operator, context

def rectangle(xSize, ySize, **kwargs):
    """
    Creates a rectangle with sides along global x and y axis
    """
    return context.factory["Rectangle"](xSize, ySize, **kwargs)

class Rectangle(Operator):
    def __init__(self, xSize, ySize, **kwargs):
        self.replace = False
        self.xSize = xSize
        self.ySize = ySize
        # apply kwargs
        for k in kwargs:
            setattr(self, k, kwargs[k])
        super().__init__()