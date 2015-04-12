import bmesh
import pro
from pro import context
from .shape import Shape2d

class Copy(pro.op_copy.Copy):
    def execute(self):
        shape = context.getState().shape
        # only 2D shapes can be copied at the moment!
        if not isinstance(shape, Shape2d): return
        
        duplicate = bmesh.ops.duplicate(context.bm, geom = (shape.face,))
        copiedFace = [entry for entry in duplicate["geom"] if isinstance(entry, bmesh.types.BMFace)][0]
        constructor = type(shape)
        copiedShape = constructor(copiedFace.loops[0])
        
        if self.operator:
            context.pushState(shape=copiedShape)
            self.operator.execute()
            context.popState()