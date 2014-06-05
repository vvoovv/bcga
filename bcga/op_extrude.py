import bpy
import cga
from cga import context

class Extrude(cga.op_extrude.Extrude):
	def execute(self):
		print("extrude", self.height)
		bpy.ops.object.mode_set(mode="EDIT")
		bpy.ops.mesh.select_all(action="SELECT")
		bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={"value":(0, 0, self.height)})
		bpy.ops.mesh.select_all(action="DESELECT")
		# without setting mode to "OBJECT" the number of polygons, edges and vertices isn't updated
		bpy.ops.object.mode_set(mode="OBJECT")
