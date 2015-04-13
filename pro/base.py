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


def countOperator(o):
	"""
	A helper function that checks if its argument must be counted as Prokitektura Operator
	in a constructor of the other operators. Every operator can be counted once.
	The function also sets count attribute to False in the positive case when it returns True
	
	Returns:
	    bool: True if the operator must be counted, False otherwise
	"""
	if isinstance(o, Operator) and o.count:
		result = True
		o.count = False
	else:
		result = False
	return result


class Operator:
	def __init__(self):
		# Every operator can be counted once time in a constructor of the other operators
		# self.count is set to False in the countOperator helper function
		self.count = True
		context.operator.addChildOperator(self)
	
	def __rrshift__(self, value):
		# The operator to be returned.
		# We create a wrapper RrshiftOperator if >> already was applied to the operator instance
		wrapper = False
		if hasattr(self, "value"):
			operator = RrshiftOperator(self)
			wrapper = True
		else:
			operator = self
		if isinstance(value, Modifier):
			setattr(operator, value.modifier, True)
			operator.value = value.value
			if wrapper:
				wrapper.modifier = value.modifier
		elif isinstance(value, Param):
			operator.value = value.value
		else:
			operator.value = value
		return operator
	
	def execute(self):
		pass
	
	def execute_join(self, band):
		""" This method should be called for each band of rectangles after join(..) finished its procession"""
		pass
	
	def __call__(self):
		# NOTE: the line context.operator.addChildOperator(self) was required before
		# to avoid error.
		# Now that line causes eroor, so it was commented out
		#context.operator.addChildOperator(self)
		return self
	
	def __str__(self):
		return self.__class__.__name__


class RrshiftOperator:
	"""A wrapper class to support multiple usage of operators with >>"""
	def __init__(self, operator):
		# operator has been alread counted
		self.count = False
		self.modifier = None
		self.operator = operator
	
	def execute(self):
		operator = self.operator
		# remember original value for self.operator
		value = self.value
		operator.value = self.value
		self.operator.execute()
		if self.modifier:
			delattr(operator, self.modifier)
		# restore the original value
		operator.value = value
		if self.modifier:
			setattr(operator, self.modifier, True)


class ComplexOperator(Operator):
	def __init__(self, numParts):
		# remove numParts operators from
		context.operator.removeChildOperators(numParts) 
		super().__init__()


class Rule(ComplexOperator):
	
	def __init__(self, operator, args, kwargs):
		self.operator = operator
		self.args = args
		self.kwargs = kwargs
		# count how many Prokitektura operators we have in args and kwargs
		numParts = 0
		for arg in args:
			if countOperator(arg):
				numParts += 1
		for k in kwargs:
			if countOperator(kwargs[k]):
				numParts += 1
		# list of child operators
		self.operators = []
		super().__init__(numParts)
	
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
	
	def __call__(self):
		self.reset()
	
	def addAttribute(self, attr, value):
		setattr(self, attr, value)
		self.attrs.append(attr)
	
	def removeAttributes(self):
		for attr in self.attrs:
			delattr(self, attr)
		self.attrs = []
	
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
		
	def init(self):
		# implementation specific attributes
		self.attrs = []
		# stack to track branching
		self.stack = []
		self.deferreds = []
		# the list of params
		self.params = []
	
	def prepare(self):
		"""The method does all necessary preparations for a rule evaluation."""
		# set random values for the random params from self.params
		for param in self.params:
			if param.random:
				param.assignValue()
	
	def addDeferred(self, shape, deferredOperator):
		self.deferreds.append((shape, deferredOperator))
	
	def executeDeferred(self):
		self.joinManager = self.joinManager()
		for entry in self.deferreds:
			# entry[1] is operator
			# entry[0] is shape
			entry[1].resolve(entry)
		self.joinManager.finalize()


def shape():
	context.operator.executeChildOperators()
	return context.getState().shape


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