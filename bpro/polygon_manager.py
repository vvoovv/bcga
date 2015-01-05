from pro.base import Operator

class Manager:
    """A helper class for bpro.polygon.Polygon"""
    def __init__(self):
        # a list of tuples (shape, rule_to_be_executed_for_the_shape)
        self.shapes = []
        # default rule
        self.rule = None
    
    def getValue(self, obj):
        return obj.value if isinstance(obj, Operator) else obj
    
    def resolve(self, shape, value=None):
        rule = value if isinstance(value, Operator) else (self.rule if self.rule else None)
        if rule:
            self.shapes.append((shape, rule))