import imp, os, inspect
import bpy, bmesh

from pro import context

from bpro.op_decompose import Decompose
from .op_split import Split
from .op_extrude import Extrude
from .op_color import Color
from .op_texture import Texture

from pro.base import Param

from .shape import getInitialShape


def buildFactory():
	factory = context.factory
	factory["Decompose"] = Decompose
	factory["Split"] = Split
	factory["Extrude"] = Extrude
	factory["Color"] = Color
	factory["Texture"] = Texture

def apply(ruleFile, startRule="Lot"):
	# setting the path to the rule for context
	context.ruleFile = ruleFile if isinstance(ruleFile, str) else ruleFile.__file__
	params = None
	mesh = bpy.context.object.data
	# create a uv layer for the mesh
	# TODO: a separate pass through the rules is needed to find out how many uv layers are needed 
	mesh.uv_textures.new(Texture.defaultLayer)
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
	context.init(getInitialShape(context.bm))
	
	if isinstance(ruleFile, str):
		# remove extension from ruleFile if it was provided
		ruleFile = os.path.splitext(ruleFile)[0]
		moduleName = os.path.basename(ruleFile)
		_file, _pathname, _description = imp.find_module(moduleName, [os.path.dirname(ruleFile)])
		module = imp.load_module(moduleName, _file, _pathname, _description)
		_file.close()

		# prepare context internal stuff
		context.prepare()
		# params is a list of tuples: (paramName, instanceofParamClass)
		params = [m for m in inspect.getmembers(module, isParam)]
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
	
	return (module, params)

def isParam(member):
	"""A predicate for the inspect.getmembers call"""
	return isinstance(member, Param)

buildFactory()