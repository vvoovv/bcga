import pro
from pro import context

class Split(pro.op_split.Split):
	def execute(self):
		state = context.getState()
		shape = state.shape
		
		# Calculate cuts.
		# cuts is a list of tuples (cutShape, ruleForTheCutShape)
		cuts = shape.split(self.direction, self.parts)
		
		# apply the rule for each cut
		for splitIndex,cut in enumerate(cuts):
			context.pushState(shape=cut[0])
			cut[1].execute()
			context.popState()