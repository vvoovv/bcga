import bpy, bmesh
import cga
from cga import context

class Extrude(cga.op_extrude.Extrude):
	def execute(self):
		bm = context.bm
		geom = bmesh.ops.extrude_face_region(bm, geom=bm.faces)
		# get extruded vertices
		verts = [v for v in geom["geom"] if isinstance(v, bmesh.types.BMVert)]
		bmesh.ops.translate(bm, verts=verts, vec=(0, 0, self.height))
