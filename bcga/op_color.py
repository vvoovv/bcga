import bpy
import cga
from cga import context

# a dict to cache Blender material for each color
materialCache = {}

class Color(cga.op_color.Color):
	def execute(self):
		print("color", self.color)
		color = self.color
		if color in materialCache:
			material = materialCache[color]
		else:
			material = bpy.data.materials.new(str(color))
			material.diffuse_color = color
			# remember the color for the future use
			materialCache[color] = material
		bpy.context.active_object.data.materials.append(material)