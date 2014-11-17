from .base import ComplexOperator, context

front = "front"
back = "back"
left = "left"
right = "right"
top = "top"
bottom = "bottom"
side = "side"
all = "all"

def decompose(*parts):
	return context.factory["Decompose"](*parts)

class Decompose(ComplexOperator):
	def __init__(self, *parts):
		self.parts = parts
		super().__init__(len(parts))
