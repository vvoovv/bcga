from .base import Operator, context

def extrude(depth):
	return context.factory["Extrude"](depth)

class Extrude(Operator):
	def __init__(self, depth):
		# depth may be an instance of ParamFloat, so cast it to float
		self.depth = float(depth)
		self.keepOriginal = False
		super().__init__()