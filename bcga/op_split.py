import cga
from cga import context

class Split(cga.op_split.Split):
	def execute(self, operatorDef):
		super().execute(operatorDef)
