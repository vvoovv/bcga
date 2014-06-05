from .base import Operator, context

def extrude(height):
	return context.factory["Extrude"](height)

class Extrude(Operator):
	def __init__(self, height):
		self.height = height
		super().__init__()