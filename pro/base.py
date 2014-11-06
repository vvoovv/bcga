import random as randomlib

def flt(value=1):
	return Modifier(flt=value)

def rel(value):
	return Modifier(rel=value)


class Modifier:
	"""
	A wrapper for flt(...) and rel(...) modifiers
	"""
	def __init__(self, **kwargs):
		for k in kwargs:
			# there is only one kwarg!
			self.modifier = k
			setattr(self, k, True)
			self.value = kwargs[k]
	
	def execute(self):
		pass
			

class Operator:
	def __init__(self):
		context.operator.addChildOperator(self)
	
	def __rrshift__(self, value):
		if isinstance(value, Modifier):
			setattr(self, value.modifier, True)
			self.value = value.value
		elif isinstance(value, Param):
			self.value = value.value
		else:
			self.value = value
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
		# list of child operators
		self.operators = []
		super().__init__()
	
	def execute(self):
		# setting the current operator to self
		context.operator = self
		self.operator(*self.args, **self.kwargs)
		self.executeChildOperators()

	def addChildOperator(self, operator):
		"""Adds child operator"""
		self.operators.append(operator)
	
	def removeChildOperators(self, numOperators):
		while numOperators:
			self.operators.pop()
			numOperators -= 1
	
	def executeChildOperators(self):
		# execute operators inside the body of the current operator
		for o in self.operators:
			o.execute()
		self.operators.clear()
	
	def __str__(self):
		return self.operator.__name__


class ComplexOperator(Operator):
	def __init__(self, numParts):
		# remove numParts operators from
		context.operator.removeChildOperators(numParts) 
		super().__init__()


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


class State:
	def __init__(self, **kwargs):
		for k in kwargs:
			setattr(self, k, kwargs[k])
		self.valid = True


class Context:
	def __init__(self):
		self.reset()
		
	def reset(self):
		# the factory stores references to the basic classes
		self.factory = {}
		# stack to track branching
		self.stack = list()
	
	def __call__(self):
		self.reset()
	
	def getState(self):
		return self.stack[-1]
	
	def pushState(self, **kwargs):
		# create a new execution state entry
		state = State(**kwargs)
		self.stack.append(state)
		return state
	
	def popState(self):
		self.stack.pop()
	
	def registerParam(self, param):
		self.params.append(param)
		
	def init(self, shape):
		# the list of params
		self.params = []
		# push the initial state with the initial shape to the execution stack
		self.pushState(shape=shape)
	
	def prepare(self):
		"""The method does all necessary preparations for a rule evaluation."""
		# set random values for the random params from self.params
		for param in self.params:
			if param.random:
				param.assignValue()

#
# Parameters stuff
#

def param(value):
	if isinstance(value, str) and value[0]=="#":
		result = ParamColor(value)
	else:
		result = ParamFloat(value)
	return result

def random(low, high):
	return Random(low, high)


class Param:
	def setValue(self, value):
		self.value = value
	
	def getValue(self):
		return self.value

	def execute(self):
		pass


class ParamFloat(Param):
	def __init__(self, value):
		if (isinstance(value, Random)):
			self.value = None
			self.random = value
		else:
			self.value = value
			self.random = None
		context.registerParam(self)
	
	def assignValue(self):
		"""Assigns a value for the parameter. Relevant only for random parameters"""
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
	
	def __neg__(self):
		return -self.value
	
	def __abs__(self):
		return abs(self.value)


class ParamColor(Param):
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