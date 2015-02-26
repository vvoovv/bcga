import pro
from pro import context
from .polygon import Roof
from .polygon_manager import Manager

class HipRoof(pro.op_hip_roof.HipRoof):
    def execute(self):
        shape = context.getState().shape
        face = shape.face
        self.init(len(face.verts))
        manager = Manager()
        roof = Roof(face.verts, shape.getNormal(), manager)
        # soffits
        if self.soffits:
            manager.rule = self.soffit
            roof.inset(*self.soffits, negate=True)
        # fascias
        if self.fasciaSize:
            manager.rule = self.fascia
            roof.translate(self.fasciaSize)
        # hip roof itself
        manager.rule = self.face
        roof.roof(*self.pitches)
        shape.delete()
        # finalizing: if there is a rule for the shape, execute it
        for entry in manager.shapes:
            context.pushState(shape=entry[0])
            entry[1].execute()
            context.popState()
        
        