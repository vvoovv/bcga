import bmesh, mathutils
import pro
from pro import context
from .shape import Shape2d, rotation_zNormal_xHorizontal


class Translate(pro.op_translate.Translate):
    def execute(self):
        shape = context.getState().shape
        # only 2D shapes can be translated at the moment!
        if not isinstance(shape, Shape2d): return
        # rotation matrix, note True as the third parameter to rotation_zNormal_xHorizontal(..)
        matrix = rotation_zNormal_xHorizontal(shape.firstLoop, shape.getNormal(), True)
        bmesh.ops.translate(context.bm, verts=shape.face.verts, vec=matrix * mathutils.Vector(self.vec))