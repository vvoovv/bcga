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
            if self.overhang:
                for _shape in roof.insets:
                    context.pushState(shape=_shape)
                    self.overhang.execute()
                    context.popState()
        if self.fasciaSize:
            roof.translate(self.fasciaSize)
            if self.fascia:
                for _shape in roof.translated:
                    context.pushState(shape=_shape)
                    self.fascia.execute()
                    context.popState()
        roof.roof(*self.pitches)
        shape.delete()
        if self.face:
            for _shape in roof.faces:
                context.pushState(shape=_shape)
                self.face.execute()
                context.popState()
        