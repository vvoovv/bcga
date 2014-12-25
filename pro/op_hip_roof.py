from .base import Operator, ComplexOperator, context, countOperator

def hip_roof(*args, **kwargs):
    return context.factory["HipRoof"](*args, **kwargs)


class HipRoof(ComplexOperator):
    def __init__(self, *args, **kwargs):
        self.args = args
        self.overhangSize = None
        self.fasciaSize = None
        if "fasciaSize" in kwargs:
            self.fasciaSize = kwargs["fasciaSize"]
        self.face = None
        self.overhang = None
        self.fascia = None
        # find all definitions of operator and how many numerical values we have
        numOperators = 0
        i = len(args) - 1
        while i>0:
            arg = args[i]
            if isinstance(arg, Operator):
                setattr(self, arg.value, arg)
                numOperators += 1
            else:
                self.numValues = i + 1
                break
            i -= 1

        super().__init__(numOperators)
    
    def init(self, numEdges):
        args = self.args
        numValues = self.numValues
        overhangs = None
        if numValues>2:
            pitches = []
            if numValues==2*numEdges:
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
            if numValues==2:
                overhangs = (-args[1],)
            elif self.overhangSize:
                overhangs = (self.overhangSize,)
        self.overhangs = overhangs
        self.pitches = pitches
