from .base import ComplexOperator, context

#faces
f = "f"
#edges
e = "e"
#vertices
v = "v"

front = "front"
side = "side"
top = "top"

from .base import ComplexOperator, context

def comp(compSelector):
	return context.factory["Comp"](compSelector)

class Comp(ComplexOperator):
	def __init__(self, compSelector):
		self.compSelector = compSelector
		super().__init__()
