from .base import ComplexOperator, context

#faces
f = "f"
#edges
e = "e"
#vertices
v = "v"

front = "front"
back = "back"
left = "left"
right = "right"
top = "top"
bottom = "bottom"
side = "side"
all = "all"

from .base import ComplexOperator, context

def decompose(selector=None):
	return context.factory["Decompose"](selector)

class Decompose(ComplexOperator):
	def __init__(self, selector):
		self.selector = selector
		super().__init__()
