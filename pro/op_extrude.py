from .base import Operator, context

def extrude(depth):
	return context.factory["Extrude"](depth)

class Extrude(Operator):
	def __init__(self, depth):
		self.depth = depth
		super().__init__()