from .base import ComplexOperator, context

def split(direction):
	return context.factory["Split"](direction)

class Split(ComplexOperator):
	def __init__(self, direction):
		self.direction = direction
		super().__init__()
	
	def execute(self, operatorDef):
		state = context.getExecutionState()
		if not state['valid']:
			print("split",  self.direction, "invalid state")
		print("executing split", self.direction)
		print(operatorDef)
		# invalidate state
		state['valid'] = False
