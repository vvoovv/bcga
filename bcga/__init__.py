import imp, os
import bpy

from cga import context

from .op_comp import Comp
from .op_split import Split
from .op_extrude import Extrude
from .op_color import Color

def parent_set():
	# perform parenting of the active object and selected objects
	bpy.ops.object.parent_set()
	# deselect everything
	bpy.ops.object.select_all(action="DESELECT")

def buildFactory():
	factory = context.factory
	factory["Comp"] = Comp
	factory["Split"] = Split
	factory["Extrude"] = Extrude
	factory["Color"] = Color

def apply(ruleFile, startRule="Lot"):
	# remove extension from ruleFile if it was provided
	ruleFile, fileExtension = os.path.splitext(ruleFile)
	_file, _pathname, _description = imp.find_module(os.path.basename(ruleFile), [os.path.dirname(ruleFile)])
	module = imp.load_module("simple01", _file, _pathname, _description)
	getattr(module, startRule)()

buildFactory()