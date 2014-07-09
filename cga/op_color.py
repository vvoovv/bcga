from .base import Operator, context

def color(_color):
	return context.factory["Color"](_color)

class Color(Operator):
	def __init__(self, _color):
		if isinstance(_color, str):
			self.colorHex = _color
			# we've got a hex string, convert to the tuple
			_color = tuple( map(lambda c: c/255, bytes.fromhex(_color[-6:])) )
		self.color = _color
		super().__init__()