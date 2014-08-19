import pro
from pro import context

class Decompose(pro.op_decompose.Decompose):
	
	def execute(self):
		state = context.getState()
		
		# create a dict from the operatorDef list
		parts = {}
		for part in self.parts:
			parts[part.value] = part
		
		# components is a dictionary with a comp-selector as the key and a list of 2D-shapes as the related value 
		components = state.shape.comp(parts)
		if len(components)>0:
			# now apply the rule for each decomposed 2D-shape
			for selector in components:
				for _shape in components[selector]:
					context.pushState(shape=_shape)
					parts[selector].execute()
					context.popState()