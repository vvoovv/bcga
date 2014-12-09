import pro
from pro import context
from .op_decompose import decompose_execute

class Extrude(pro.op_extrude.Extrude):
	def execute(self):
		state = context.getState()
		shape = state.shape.extrude(self)
		if self.parts:
			decompose_execute(shape, self.parts)
		else:
			state.shape = shape
	
	def execute_join(self, band):
		band.extrude()