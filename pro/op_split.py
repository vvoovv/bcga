from .base import Operator, ComplexOperator
from .base import context

def split(direction, *parts, **kwargs):
	"""
	Splits a 2D-shape into a number of shapes.
	
	Args:
		direction: Split direction, currently x or y
		*parts: Split definitions
	
	Kwargs:
		reverse (bool): Split definitions are processed in the reversed order.
			The default value is False.
	"""
	return context.factory["Split"](direction, *parts, **kwargs)

class Split(ComplexOperator):
	def __init__(self, direction, *parts, **kwargs):
		self.direction = direction
		self.reverse = False
		self.parts = parts
		# apply kwargs
		for k in kwargs:
			setattr(self, k, kwargs[k])
		super().__init__(getNumOperators(parts))


class SplitDef:
	def __init__(self, parts, repeat):
		self.parts = []
		for part in parts:
			# if isinstance(part, tuple), then part is a repeat clause
			part = SplitDef(part, True) if isinstance(part, tuple) else part
			self.parts.append(part)
		self.repeat = repeat
		self.childRepeat = None
		self.hasFloating = False


class RawValue:
	"""
	A wrapper for raw float or integer split value without an operator or a rule.
	"""
	def __init__(self, value):
		self.value = value
	
	def execute(self):
		pass


def calculateSplit(splitDef, scopeSise, parentSplitDef=None):
	if not parentSplitDef:
		splitDef = SplitDef(splitDef, False)
	fixedSize = 0
	floatingSize = 0
	for partIndex, part in enumerate(splitDef.parts):
		if isinstance(part, SplitDef):
			# only one repeat is allowed!
			if not splitDef.repeat and not splitDef.childRepeat:
				# notify parent splitDef that it has repeat
				splitDef.childRepeat = part
			calculateSplit(part, scopeSise, splitDef)
		else:
			if isinstance(part, float) or isinstance(part, int):
				part = RawValue(part)
				splitDef.parts[partIndex] = part
			value = part.value
			if hasattr(part, "flt"):
				_value = value/scopeSise
				part._value = _value
				floatingSize += _value
				if not splitDef.hasFloating:
					splitDef.hasFloating = True
				if parentSplitDef and not parentSplitDef.hasFloating:
					# notify parent splitDef that it has floating
					parentSplitDef.hasFloating = True
			elif hasattr(part, "rel"):
				fixedSize += value
				part._value = value
			else:
				_value = value/scopeSise
				part._value = _value
				fixedSize += _value
	splitDef.fixedSize = fixedSize
	splitDef.floatingSize = floatingSize
	
	if not parentSplitDef:
		# perform final calculations
		# number of repetitions
		numRepetitions = 0
		# multiplier for floating
		multiplier = 0
		if splitDef.childRepeat:
			# the child splitDef has repeat
			if splitDef.hasFloating:
				childRepeat = splitDef.childRepeat
				# number of repetions
				numRepetitions = (1-floatingSize-fixedSize)/(childRepeat.floatingSize+childRepeat.fixedSize)
				if numRepetitions<=0:
					numRepetitions = 0
				elif numRepetitions<1:
					numRepetitions = 1
				else:
					numRepetitions = round(numRepetitions)
				# calculating multiplier for floating
				if numRepetitions>0 or floatingSize>0:
					multiplier = (1-fixedSize-numRepetitions*childRepeat.fixedSize)/(floatingSize+numRepetitions*childRepeat.floatingSize)
		elif floatingSize>0:
			# no repeats but there are floating
			multiplier = (1-fixedSize)/floatingSize
		
		if multiplier<0:
			# no space for floating
			multiplier = 0
		
		# calculating cuts
		cuts = []
		lastCutValue = 0
		for part in splitDef.parts:
			if part == splitDef.childRepeat:
				for cutIndex in range(numRepetitions):
					for _part in part.parts:
						lastCutValue = assignCut(cuts, _part, multiplier, lastCutValue)
			else:
				lastCutValue = assignCut(cuts, part, multiplier, lastCutValue)
				if lastCutValue == 1:
					break
		# finished!
		
		# printing cut sizes
		#_cuts = [cut[0] for cut in cuts]
		#_lastCut = 0
		#for i,_cut in enumerate(_cuts):
		#	cutSize = scopeSise*(_cuts[i]-_lastCut)
		#	_lastCut = _cuts[i]
		#	_cuts[i] = cutSize
		#print(_cuts)
		return cuts

def assignCut(cuts, part, multiplier, lastCutValue):
	cutSize = part._value
	if hasattr(part, "flt"):
		cutSize = cutSize*multiplier if multiplier>0 else 0
	if cutSize>0:
		lastCutValue += cutSize
		if lastCutValue>1:
			lastCutValue = 1
		# the element of the list (lastCutValue, 0, part) with index 1 is reserved for the related shape to be created later
		cuts.append([lastCutValue, None, part])
	return lastCutValue

def getNumOperators(parts):
	"""
	An auxiliary function to calculate the number of operators in parts list
	"""
	numOperators = 0
	for p in parts:
		if isinstance(p, Operator):
			if p.count:
				p.count = False
				numOperators += 1
		elif isinstance(p, tuple):
			# this is the case of repeat(...) modifier
			numOperators += getNumOperators(p)
	return numOperators