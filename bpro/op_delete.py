from pro.base import Operator

class Delete(Operator):
    
    def __init__(self):
        super().__init__()
    
    def execute(self):
        shape = context.getState().shape
        shape.delete()