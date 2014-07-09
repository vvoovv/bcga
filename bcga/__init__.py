import imp, os
import bpy, bmesh

from cga import context

from .op_comp import Comp
from .op_split import Split
from .op_extrude import Extrude
from .op_color import Color


def buildFactory():
	factory = context.factory
	factory["Comp"] = Comp
	factory["Split"] = Split
	factory["Extrude"] = Extrude
	factory["Color"] = Color

def apply(ruleFile, startRule="Lot"):
	mesh = bpy.context.active_object.data
	# all operations will be done in the EDIT mode
	bpy.ops.object.mode_set(mode="EDIT")
	# setting bmesh instance
	context.bm = bmesh.from_edit_mesh(mesh)
	# list of unused faces for removal
	context.facesForRemoval = []
	
	# remove extension from ruleFile if it was provided
	ruleFile, fileExtension = os.path.splitext(ruleFile)
	_file, _pathname, _description = imp.find_module(os.path.basename(ruleFile), [os.path.dirname(ruleFile)])
	module = imp.load_module("simple01", _file, _pathname, _description)
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
	# cleaning context from blender specific members
	delattr(context, "bm")
	delattr(context, "facesForRemoval")

buildFactory()