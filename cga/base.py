import random as randomlib

class Operator:
	def __init__(self):
		if context.immediateExecution:
			self.execute()
	
	def __rrshift__(self, value):
		self.value = value.value if isinstance(value, Attr) else value
		return self
	
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

	def into(self, *args):
		self.parts = args
		if self.immediateExecution:
			# remove immediate execution lock
			context.immediateExecution = True
			self.execute()
		return self


class OperatorDef:
	def __init__(self, *operators):
		self.parts = list(operators)
		self.repeat = False
	
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
	
	def pushExecutionState(self, **kwargs):
		# create a new execution state entry
		state = kwargs
		state['valid'] = True
		self.stack.append(state)
		return state
	
	def popExecutionState(self):
		self.stack.pop()
	
	def registerAttr(self, attr):
		self.attrs.append(attr)
		
	def init(self):
		# the list of attrs
		self.attrs = []
	
	def prepare(self):
		"""The method does all necessary preparations for a rule evaluation."""
		# set random values for the random attrs from self.attrs
		for attr in self.attrs:
			if attr.random:
				attr.assignValue()

#
# Attributes stuff
#

def attr(value):
	if isinstance(value, str) and value[0]=="#":
		result = AttrColor(value)
	else:
		result = AttrFloat(value)
	return result

def random(low, high):
	return Random(low, high)


class Attr:
	def setValue(self, value):
		self.value = value
	
	def getValue(self):
		return self.value


class AttrFloat(Attr):
	def __init__(self, value):
		if (isinstance(value, Random)):
			self.value = None
			self.random = value
		else:
			self.value = value
			self.random = None
		context.registerAttr(self)
	
	def assignValue(self):
		"""Assigns a value for the attribute. Relevant only for random attributes"""
		if self.random:
			self.value = randomlib.uniform(self.random.low, self.random.high)
	
	def __float__(self):
		return float(self.value)
	
	def __add__(self, other):
		return self.value + other
	
	def __radd__(self, other):
		return other + self.value
	
	def __sub__(self, other):
		return self.value - other
	
	def __rsub__(self, other):
		return other - self.value
	
	def __mul__(self, other):
		return self.value * other
	
	def __rmul__(self, other):
		return other * self.value
	
	def __truediv__(self, other):
		return self.value/other
	
	def __rtruediv__(self, other):
		return other/self.value


class AttrColor(Attr):
	def __init__(self, value):
		self.value = value
	
	def __str__(self):
		return self.value
	
	def getValue(self):
		# convert from the hex string to a tuple
		return tuple( map(lambda c: c/255, bytes.fromhex(self.value[-6:])) )
	
	def setValue(self, value):
		# convert from the tuple to a hex string
		self.value = "#%02x%02x%02x" % tuple( map(lambda c: round(c*255), value) )

class Random:
	def __init__(self, low, high):
		self.low = low
		self.high = high


context = Context()