import bpy
import cga
from cga import context

# a dict to cache Blender material for each color
materialCache = {}

class Color(cga.op_color.Color):
	def execute(self):
		colorHex = self.colorHex
		if colorHex in materialCache:
			materialIndex = materialCache[colorHex]
		else:
			materialIndex = len(bpy.context.active_object.data.materials)
			material = bpy.data.materials.new(colorHex)
			material.diffuse_color = self.color
			# remember the color for the future use
			materialCache[colorHex] = materialIndex
			bpy.context.active_object.data.materials.append(material)
		# assign material to the bmesh face
		shape = context.getExecutionState()['shape']
		shape.material_index = materialIndex