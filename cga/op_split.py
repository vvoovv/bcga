import math
from .base import ComplexOperator, OperatorDef
from .base import context

def split(direction):
	return context.factory["Split"](direction)

class Split(ComplexOperator):
	def __init__(self, direction):
		self.direction = direction
		super().__init__()
	
	def execute(self):
		operatorDef = self.operatorDef
		state = context.getExecutionState()
		if not state['valid']:
			print("split",  self.direction, "invalid state")
		print("executing split", self.direction)
		print(operatorDef)
		# invalidate state
		state['valid'] = False

def calculateSplit(splitDef, scopeSise, parentSplitDef=None):
	splitDef.childRepeat = None
	splitDef.hasFloating = False
	fixedSize = 0
	floatingSize = 0
	for part in splitDef.parts:
		if isinstance(part, OperatorDef):
			# only one repeat is allowed!
			if part.repeat and not splitDef.repeat and not splitDef.childRepeat:
				# notify parent splitDef that it has repeat
				splitDef.childRepeat = part
			calculateSplit(part, scopeSise, splitDef)
		else:
			value = part.value
			if isinstance(value, dict):
				if "flt" in value:
					_value = value["flt"]/scopeSise
					part._value = _value
					part.flt = True
					floatingSize += _value
					if not splitDef.hasFloating:
						splitDef.hasFloating = True
					if not parentSplitDef.hasFloating:
						# notify parent splitDef that it has floating
						parentSplitDef.hasFloating = True
				elif "rel" in value:
					fixedSize += value["rel"]
					part._value = value["rel"]
			else:
				_value = value/scopeSise
				part._value = _value
				fixedSize += value/scopeSise
	splitDef.fixedSize = fixedSize
	splitDef.floatingSize = floatingSize
	
	if not parentSplitDef:
		# perform final calculations
		# number of repetitions
		numRepetitions = 0
		# multiplier for floating
		multiplier = 0
		# the parent splitDef has repeat
		if splitDef.repeat:
			if splitDef.hasFloating:
				# number of repetions
				numRepetitions = 1/(floatingSize+fixedSize)
				numRepetitions = round(numRepetitions)
				# calculating multiplier for floating
				multiplier = (1-numRepetitions*fixedSize)/(numRepetitions*floatingSize)
		# the child splitDef has repeat
		elif splitDef.childRepeat:
			if splitDef.hasFloating:
				childRepeat = splitDef.childRepeat
				# number of repetions
				numRepetitions = (1-floatingSize-fixedSize)/(childRepeat.floatingSize+childRepeat.fixedSize)
				numRepetitions = round(numRepetitions)
				# calculating multiplier for floating
				multiplier = (1-fixedSize-numRepetitions*childRepeat.fixedSize)/(floatingSize+numRepetitions*childRepeat.floatingSize)
		
		if multiplier<0:
			# no space for floating
			multiplier = 0
		print(numRepetitions, multiplier)
		# calculating cuts
		cuts = []
		lastCutValue = 0
		# the parent splitDef has repeat
		if splitDef.repeat:
			for cutIndex in range(numRepetitions):
				for part in splitDef.parts:
					lastCutValue = assignCut(cuts, part, multiplier, lastCutValue)
		else:
			for part in splitDef.parts:
				if part == splitDef.childRepeat:
					for cutIndex in range(numRepetitions):
						for _part in part.parts:
							lastCutValue = assignCut(cuts, _part, multiplier, lastCutValue)
				else:
					lastCutValue = assignCut(cuts, part, multiplier, lastCutValue)
		# finished!
		print(cuts)
		return cuts

def assignCut(cuts, part, multiplier, lastCutValue):
	cutSize = part._value
	if hasattr(part, "flt"):
		cutSize = cutSize*multiplier if multiplier>0 else 0
	if cutSize>0:
		lastCutValue += cutSize
		cuts.append((lastCutValue, part))
	return lastCutValue