from .base import ComplexOperator, context, countOperator

def hip_roof(*args, **kwargs):
    return context.factory["HipRoof"](*args, **kwargs)


class HipRoof(ComplexOperator):
    def __init__(self, *args, **kwargs):
        self.overhang = False
        self.fascia = False
        if "fasciaSize" in kwargs:
            self.fascia = True
            self.fasciaSize = kwargs["fasciaSize"]
        numArgs = len(args)
        self.pitch = args[0]
        if numArgs==2:
            self.overhang = True
            self.overhangSize = args[1]
        super().__init__(0)
            
        