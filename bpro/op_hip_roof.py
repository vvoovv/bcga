import pro
from pro import context
from .polygon import Roof

class HipRoof(pro.op_hip_roof.HipRoof):
    def execute(self):
        shape = context.getState().shape
        face = shape.face
        roof = Roof(face.verts, face.normal)
        if self.overhang:
            roof.inset(-self.overhangSize)
        if self.fascia:
            roof.translate(self.fasciaSize)
        roof.roof(self.pitch)
        shape.delete()
        