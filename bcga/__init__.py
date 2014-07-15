import imp, os, inspect
import bpy, bmesh

from cga import context

from .op_comp import Comp
from .op_split import Split
from .op_extrude import Extrude
from .op_color import Color

from cga.base import Attr


def buildFactory():
	factory = context.factory
	factory["Comp"] = Comp
	factory["Split"] = Split
	factory["Extrude"] = Extrude
	factory["Color"] = Color

def apply(ruleFile, startRule="Lot"):
	attrs = None
	mesh = bpy.context.active_object.data
	# all operations will be done in the EDIT mode
	enableEditMode = bpy.context.mode != "EDIT_MESH"
	bpy.ops.object.mode_set(mode="EDIT")
	# setting bmesh instance
	context.bm = bmesh.from_edit_mesh(mesh)
	# list of unused faces for removal
	context.facesForRemoval = []
	# a dict to cache Blender material for each color
	context.materialCache = {}
	# initialize the context
	context.init()
	
	if isinstance(ruleFile, str):
		# remove extension from ruleFile if it was provided
		ruleFile, fileExtension = os.path.splitext(ruleFile)
		moduleName = os.path.basename(ruleFile)
		_file, _pathname, _description = imp.find_module(moduleName, [os.path.dirname(ruleFile)])
		module = imp.load_module(moduleName, _file, _pathname, _description)

		# prepare context internal stuff
		context.prepare()
		# attrs is a list of tuples: (attrName, instanceofAttrClass)
		attrs = [m for m in inspect.getmembers(module, isAttr)]
	else:
		# ruleFile is actually a module
		module = ruleFile
	
	# evaluate the rule set
	getattr(module, startRule)()
	
	# remove unused faces from context.facesForRemoval
	for face in context.facesForRemoval:
		context.bm.faces.remove(face)
	# remove doubles
	bpy.ops.mesh.select_all(action="SELECT")
	bpy.ops.mesh.remove_doubles()
	bpy.ops.mesh.select_all(action="DESELECT")
	# update mesh
	bmesh.update_edit_mesh(mesh)
	if enableEditMode:
		# returning to the OBJECT mode
		bpy.ops.object.mode_set(mode="OBJECT")
	# cleaning context from blender specific members
	delattr(context, "bm")
	delattr(context, "facesForRemoval")
	
	return (module, attrs)

def isAttr(member):
	"""A predicate for the inspect.getmembers call"""
	return isinstance(member, Attr)

buildFactory()