import pro
from pro import context

class Split(pro.op_split.Split):
	
	def execute(self):
		shape = context.getState().shape
		
		parts = self.parts if self.reverse==False else reversed(self.parts)
		# Calculate cuts.
		# cuts is a list of tuples (cutShape, ruleForTheCutShape)
		cuts = shape.split(self.direction, parts)
		
		if len(cuts)==1:
			# degenerate case, i.e. no cut is needed
			cuts[0][2].execute()
		else:
			# apply the rule for each cut
			for cut in cuts:
				context.pushState(shape=cut[1])
				cut[2].execute()
				context.popState()