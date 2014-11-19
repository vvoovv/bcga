from .base import ComplexOperator, context, countOperator

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
		# count operators
		numOperators = 0
		for part in parts:
			if countOperator(part):
				numOperators += 1
		super().__init__(numOperators)
