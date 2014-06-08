
class Operator:
	def __init__(self):
		if context.immediateExecution:
			self.execute()
	
	def __rrshift__(self, value):
		self.value = value
		return self
	
	def __or__(self, other):
		return OperatorDef(self, other)
	
	def execute(self, *args):
		pass
	
	def __str__(self):
		return self.__class__.__name__


class Rule(Operator):
	def __init__(self, operator, args, kwargs):
		self.operator = operator
		self.args = args
		self.kwargs = kwargs
	
	def execute(self):
		self.operator(*self.args, **self.kwargs)
	
	def __str__(self):
		return self.operator.__name__


class ComplexOperator(Operator):
	def __init__(self):
		self.immediateExecution = context.immediateExecution
		if context.immediateExecution:
			# set immediate execution lock
			context.immediateExecution = False

	def into(self, operatorDef):
		self.operatorDef = operatorDef
		if self.immediateExecution:
			# remove immediate execution lock
			context.immediateExecution = True
			self.execute()
		return self


class OperatorDef:
	def __init__(self, *operators):
		self.parts = list(operators)
		self.repeat = False
	
	def __or__(self, other):
		self.parts.append(other)
		return self
	
	def __repr__(self):
		result = ""
		if self.repeat: result += "(repeat)"
		result += "["
		firstPart = True
		for part in self.parts:
			if firstPart:
				firstPart = False
			else:
				result += " | "
			result += str(part)
		result += "]"
		return result


class Context:
	def __init__(self):
		self.reset()
		
	def reset(self):
		# the factory stores references to the basic classes
		self.factory = {}
		# stack to track branching
		self.stack = list()
		self.immediateExecution = True
	
	def __call__(self):
		self.reset()
	
	def getExecutionState(self):
		if len(self.stack)==0:
			state = {'valid': True}
			self.stack.append(state)
		return self.stack[-1]
	
	def pushExecutionState(self):
		self.stack.append({'valid': True})
	
	def popExecutionState(self):
		self.stack.pop()

context = Context()