from .base import ComplexOperator, context, countOperator

def hip_roof(*args, **kwargs):
    return context.factory["HipRoof"](*args, **kwargs)


class HipRoof(ComplexOperator):
    def __init__(self, *args, **kwargs):
        self.args = args
        self.overhangSize = None
        self.fascia = False
        if "fasciaSize" in kwargs:
            self.fascia = True
            self.fasciaSize = kwargs["fasciaSize"]
        super().__init__(0)
    
    def init(self, numEdges):
        args = self.args
        numArgs = len(args)
        overhangs = None
        if numArgs>2:
            pitches = []
            if numArgs==2*numEdges:
                overhangs = []
            for i in range(numEdges):
                if overhangs is not None:
                    pitches.append(args[2*i])
                    overhangs.append(-args[2*i+1])
                else:
                    pitches.append(args[i])
            if not overhangs and self.overhangSize:
                overhangs = (self.overhangSize,)
        else:
            pitches = (args[0],)
            if numArgs==2:
                overhangs = (-args[1],)
            elif self.overhangSize:
                overhangs = (self.overhangSize,)
        self.overhangs = overhangs
        self.pitches = pitches
