from .base import ComplexOperator, context, countOperator

def extrude(depth, *parts, **kwargs):
	"""
	Extrudes a 2D-shape in the direction of the normal to the shape
	
	Args:
		depth (float): Amount of extrusion
		*parts: Definitions of decomposition parts
	
	Kwargs:
		inheritMaterialAll (bool): All created faces inherit material of the original 2D shape.
			The default value is False.
		inheritMaterialSide (bool): All but the extruded faces inherit material of the original 2D shape.
			The default value is False.
		inheritMaterialExtruded (bool): Only the extruded face inherits material of the original 2D shape.
			The default value is False.
		alwaysAlongOriginal (bool): How the first loop of each rectangular side connecting original and extruded 2D shapes is
		positioned. This option is relevant when extrude(..) is followed by join(..)
			The default value is False
	"""
	return context.factory["Extrude"](depth, *parts, **kwargs)

class Extrude(ComplexOperator):
	def __init__(self, depth, *parts, **kwargs):
		self.inheritMaterialAll = False
		self.inheritMaterialSide = False
		self.inheritMaterialExtruded = False
		self.keepOriginal = False
		self.alwaysAlongOriginal = False
		self.parts = None
		# apply kwargs
		for k in kwargs:
			setattr(self, k, kwargs[k])
		# depth may be an instance of ParamFloat, so cast it to float
		self.depth = float(depth)
		# count operators
		numOperators = 0
		for part in parts:
			if countOperator(part):
				numOperators += 1
		if len(parts):
			self.parts = parts
		super().__init__(numOperators)