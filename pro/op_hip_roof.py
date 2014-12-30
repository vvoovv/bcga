from .base import Operator, ComplexOperator, context, countOperator

def hip_roof(*args, **kwargs):
    return context.factory["HipRoof"](*args, **kwargs)


class HipRoof(ComplexOperator):
    def __init__(self, *args, **kwargs):
        self.args = args
        self.soffitSize = None
        self.fasciaSize = None
        if "fasciaSize" in kwargs:
            self.fasciaSize = kwargs["fasciaSize"]
        self.face = None
        self.soffit = None
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
        soffits = None
        if numValues>2:
            pitches = []
            if numValues==2*numEdges:
                soffits = []
            for i in range(numEdges):
                if soffits is not None:
                    pitches.append(args[2*i])
                    soffits.append(-args[2*i+1])
                else:
                    pitches.append(args[i])
            if not soffits and self.soffitSize:
                soffits = (self.soffitSize,)
        else:
            pitches = (args[0],)
            if numValues==2:
                soffits = (-args[1],)
            elif self.soffitSize:
                soffits = (self.soffitSize,)
        self.soffits = soffits
        self.pitches = pitches
