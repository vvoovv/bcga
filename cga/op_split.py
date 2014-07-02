import math
from .base import ComplexOperator, OperatorDef
from .base import context

def split(direction):
	return context.factory["Split"](direction)

class Split(ComplexOperator):
	def __init__(self, direction):
		self.direction = direction
		super().__init__()


class SplitDef:
	def __init__(self, parts, repeat):
		self.parts = []
		for i, part in enumerate(parts):
			# if isinstance(part, tuple), then part is a repeat clause
			part = SplitDef(part, True) if isinstance(part, tuple) else part
			self.parts.append(part)
		self.repeat = repeat
		self.childRepeat = None
		self.hasFloating = False


def calculateSplit(splitDef, scopeSise, parentSplitDef=None):
	if not parentSplitDef:
		splitDef = SplitDef(splitDef, False)
	fixedSize = 0
	floatingSize = 0
	for part in splitDef.parts:
		if isinstance(part, SplitDef):
			# only one repeat is allowed!
			if not splitDef.repeat and not splitDef.childRepeat:
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
					if parentSplitDef and not parentSplitDef.hasFloating:
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
		if splitDef.childRepeat:
			# the child splitDef has repeat
			if splitDef.hasFloating:
				childRepeat = splitDef.childRepeat
				# number of repetions
				numRepetitions = (1-floatingSize-fixedSize)/(childRepeat.floatingSize+childRepeat.fixedSize)
				numRepetitions = round(numRepetitions)
				# calculating multiplier for floating
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
		# finished!
		# printing cut sizes
		_cuts = [cut[0] for cut in cuts]
		_lastCut = 0
		for i,_cut in enumerate(_cuts):
			cutSize = scopeSise*(_cuts[i]-_lastCut)
			_lastCut = _cuts[i]
			_cuts[i] = cutSize
		print(_cuts)
		return cuts

def assignCut(cuts, part, multiplier, lastCutValue):
	cutSize = part._value
	if hasattr(part, "flt"):
		cutSize = cutSize*multiplier if multiplier>0 else 0
	if cutSize>0:
		lastCutValue += cutSize
		cuts.append([lastCutValue, part])
	return lastCutValue