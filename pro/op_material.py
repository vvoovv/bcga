from .base import Operator, context


def material(_material):
    return context.factory["Material"](_material)


class Material(Operator):
    def __init__(self, _material):
        self.material = _material
        super().__init__()
