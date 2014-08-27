import bpy
import pro
from pro import context

class Color(pro.op_color.Color):
	def execute(self):
		materialCache = context.materialCache
		colorHex = self.colorHex
		if colorHex in materialCache:
			materialIndex = materialCache[colorHex]
		else:
			materialIndex = len(bpy.context.object.data.materials)
			material = bpy.data.materials.new(colorHex)
			material.diffuse_color = self.color
			# remember the color for the future use
			materialCache[colorHex] = materialIndex
			bpy.context.object.data.materials.append(material)
		# assign material to the bmesh face
		shape = context.getState().shape
		shape.clearUVlayers()
		shape.face.material_index = materialIndex