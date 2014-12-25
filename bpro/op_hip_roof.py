import pro
from pro import context
from .polygon import Roof

class HipRoof(pro.op_hip_roof.HipRoof):
    def execute(self):
        shape = context.getState().shape
        face = shape.face
        self.init(len(face.verts))
        roof = Roof(face.verts, face.normal)
        if self.overhangs:
            roof.inset(*self.overhangs)
        if self.fascia:
            roof.translate(self.fasciaSize)
        roof.roof(*self.pitches)
        shape.delete()
        