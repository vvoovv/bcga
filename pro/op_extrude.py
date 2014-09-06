from .base import Operator, context

def extrude(depth):
	return context.factory["Extrude"](depth)

class Extrude(Operator):
	def __init__(self, depth):
		self.depth = depth
		self.keepOriginal = False
		super().__init__()