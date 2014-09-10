from .base import Operator, context

def extrude(depth, **kwargs):
	"""
	Extrudes a 2D-shape in the direction of the normal to the shape
	
	Args:
		depth (float): Amount of extrusion
	
	Kwargs:
		inheritMaterialAll (bool): All created faces inherit materials (textures or color) from the original 2D shape.
			The default value is False.
		inheritMaterialSides (bool): All but the extruded faces inherit materials (textures or color) from the original 2D shape.
			The default value is False.
		inheritMaterialExtruded (bool): Only the extruded face inherits materials (textures or color) from the original 2D shape.
			The default value is False.
	"""
	return context.factory["Extrude"](depth, **kwargs)

class Extrude(Operator):
	def __init__(self, depth, **kwargs):
		self.inheritMaterialAll = False
		self.inheritMaterialSides = False
		self.inheritMaterialExtruded = False
		# apply kwargs
		for k in kwargs:
			setattr(self, k, kwargs[k])
		# depth may be an instance of ParamFloat, so cast it to float
		self.depth = float(depth)
		self.keepOriginal = False
		super().__init__()