from .op_split import split

from .op_decompose import decompose
from .op_decompose import front, back, left, right, top, bottom, side, all

from .op_extrude import extrude

from .op_extrude2 import extrude2
from .op_extrude2 import middle, section, cap1, cap2, cap

from .op_color import color
from .op_texture import texture
from .op_delete import delete
from .op_join import join

from .op_hip_roof import hip_roof

from .base import flt, rel
from .base import shape
from .base import param, random
from .base import context
from .base import Rule

x = "x"
y = "y"
z = "z"

original = "original"
last = "last"

def rule(operator):
	def inner(*args, **kwargs):
			return Rule(operator, args, kwargs)
	return inner

def repeat(*args):
	return args
