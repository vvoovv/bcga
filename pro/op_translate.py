from .base import Operator, context

def translate(dx, dy, dz):
    return context.factory["Translate"]((dx, dy, dz))


class Translate(Operator):
    def __init__(self, vec):
        self.vec = vec
        super().__init__()