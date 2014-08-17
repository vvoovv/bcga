import pro
from pro import context

class Extrude(pro.op_extrude.Extrude):
	def execute(self):
		state = context.getState()
		state.shape = state.shape.extrude(self.depth)
