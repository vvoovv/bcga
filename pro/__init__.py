from .op_split import split

from pro.op_decompose import decompose
from pro.op_decompose import f, e, v
from pro.op_decompose import front, back, left, right, top, bottom, side, all

from .op_extrude import extrude
from .op_color import color
from .op_texture import texture
from .op_delete import delete

from .base import flt, rel
from .base import param, random
from .base import context
from .base import Rule

x = "x"
y = "y"
z = "z"

def rule(operator):
	def inner(*args, **kwargs):
		state = context.getState()
		if not state.valid:
			print(operator.__name__, "invalid state")
		if context.immediateExecution:
			operator(*args, **kwargs)
		else:
			return Rule(operator, args, kwargs)
	return inner

def repeat(*args):
	return args

def size(sizeX, sizeY, sizeZ):
	pass

def translate(tx, ty, tz):
	pass

def insert(assetId):
	pass
