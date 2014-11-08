from .base import ComplexOperator, context

def extrude(*args, **kwargs):
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
	return context.factory["Extrude"](*args, **kwargs)

class Extrude(ComplexOperator):
	def __init__(self, *args, **kwargs):
		self.inheritMaterialAll = False
		self.inheritMaterialSides = False
		self.inheritMaterialExtruded = False
		self.keepOriginal = False
		self.nextRule = None
		# apply kwargs
		for k in kwargs:
			setattr(self, k, kwargs[k])
		numArgs = len(args)
		numOperators = 0
		if numArgs == 1 or numArgs == 2:
			# depth may be an instance of ParamFloat, so cast it to float
			self.depth = float(args[0])
			if numArgs == 2:
				self.nextRule = args[1]
				numOperators = 1
		super().__init__(numOperators)