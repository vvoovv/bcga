bl_info = {
	"name": "Prokitektura",
	"author": "Vladimir Elistratov <vladimir.elistratov@gmail.com>",
	"version": (0, 0, 0),
	"blender": (2, 7, 0),
	"location": "View3D > Tool Shelf",
	"description": "Prokitektura implementation for Blender",
	"warning": "",
	"wiki_url": "https://github.com/prokitektura/prokitektura-blender/wiki/",
	"tracker_url": "https://github.com/prokitektura/prokitektura-blender/issues",
	"support": "COMMUNITY",
	"category": "Prokitektura",
}

import sys, os
for path in sys.path:
	if "bpro" in path:
		path = None
		break
if path:
	# we need to add path to bpro package
	sys.path.append(os.path.dirname(__file__))

import bpy
import bpro

from pro import context as proContext
from pro.base import ParamFloat, ParamColor

bpy.types.Scene.ruleFile = bpy.props.StringProperty(
	name = "Rule file",
	description = "Path to a rule file",
	subtype = "FILE_PATH"
)

class CustomFloatProperty(bpy.types.PropertyGroup):
	"""A bpy.types.PropertyGroup descendant for bpy.props.CollectionProperty"""
	value = bpy.props.FloatProperty(name="")

class CustomColorProperty(bpy.types.PropertyGroup):
	"""A bpy.types.PropertyGroup descendant for bpy.props.CollectionProperty"""
	value = bpy.props.FloatVectorProperty(name="", subtype='COLOR', min=0.0, max=1.0)

class ProMainPanel(bpy.types.Panel):
	bl_space_type = "VIEW_3D"
	bl_region_type = "TOOLS"
	#bl_context = "objectmode"
	bl_category = "Prokitektura"
	bl_label = "Main"
	
	def draw(self, context):
		scene = context.scene
		
		layout = self.layout
		box = layout.box()
		box.row().prop(scene, "ruleFile")
		box.row().operator("object.apply_pro_rule")

class Pro(bpy.types.Operator):
	bl_idname = "object.apply_pro_rule"
	bl_label = "Apply Prokitektura rule"
	bl_options = {"REGISTER", "UNDO"}
	
	collectionFloat = bpy.props.CollectionProperty(type=CustomFloatProperty)
	collectionColor = bpy.props.CollectionProperty(type=CustomColorProperty)
	
	def invoke(self, context, event):
		ruleFile = context.scene.ruleFile
		if len(ruleFile)>1 and ruleFile[:2]=="//":
			ruleFile = ruleFile[2:]
		ruleFile = os.path.join(os.path.dirname(bpy.data.filepath), ruleFile)
		if os.path.isfile(ruleFile):
			module,params = bpro.apply(ruleFile)
			self.module = module
			self.params = params
			# new params arrived, so clean all collections
			self.collectionFloat.clear()
			self.collectionColor.clear()
			# for each entry in self.params create a new item in self.collection
			for param in self.params:
				param = param[1]
				if isinstance(param, ParamFloat):
					collectionItem = self.collectionFloat.add()
				elif isinstance(param, ParamColor):
					collectionItem = self.collectionColor.add()
				collectionItem.value = param.getValue()
				param.collectionItem = collectionItem
		else:
			self.report({"ERROR"}, "The rule file %s not found" % ruleFile)
		return {"FINISHED"}
	
	def execute(self, context):
		for param in self.params:
			paramName = param[0]
			param = param[1]
			param.setValue(getattr(param.collectionItem, "value"))
		bpro.apply(self.module)
		return {"FINISHED"}
	
	def draw(self, context):
		layout = self.layout
		if hasattr(self, "params"):
			# self.params is a list of tuples: (paramName, instanceofParamClass)
			for param in self.params:
				paramName = param[0]
				row = self.layout.split()
				row.label(paramName+":")
				row.prop(param[1].collectionItem, "value")


def register():
	bpy.utils.register_module(__name__)

def unregister():
	bpy.utils.unregister_module(__name__)