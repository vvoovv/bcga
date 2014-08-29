import bpy
import pro
from pro import context

class Color(pro.op_color.Color):
	def execute(self):
		materialRegistry = context.materialRegistry
		colorHex = self.colorHex
		material = materialRegistry.getMaterial(colorHex)
		if material:
			materialIndex = materialRegistry.getMaterialIndex(colorHex)
		else:
			material = bpy.data.materials.new(colorHex)
			material.diffuse_color = self.color
			materialRegistry.setMaterial(colorHex, material)
			materialIndex = materialRegistry.getMaterialIndex(colorHex)
		# assign material to the bmesh face
		shape = context.getState().shape
		shape.clearUVlayers()
		shape.face.material_index = materialIndex