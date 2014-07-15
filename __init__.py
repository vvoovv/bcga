bl_info = {
	"name": "CGA",
	"author": "Vladimir Elistratov <vladimir.elistratov@gmail.com>",
	"version": (0, 0, 0),
	"blender": (2, 7, 0),
	"location": "View3D > Tool Shelf",
	"description": "CGA implementation for Blender",
	"warning": "",
	"wiki_url": "https://github.com/vvoovv/blender-cga/wiki/",
	"tracker_url": "https://github.com/vvoovv/blender-cga/issues",
	"support": "COMMUNITY",
	"category": "CGA",
}

import sys, os
for path in sys.path:
	if "bcga" in path:
		path = None
		break
if path:
	# we need to add path to bcga package
	sys.path.append(os.path.dirname(__file__))

import bpy
import bcga

from cga import context as cgaContext

bpy.types.Scene.ruleFile = bpy.props.StringProperty(
	name = "Rule file",
	description = "Path to a rule file",
	subtype = "FILE_PATH"
)

class CustomFloatProperty(bpy.types.PropertyGroup):
	value = bpy.props.FloatProperty(name="")

class CgaMainPanel(bpy.types.Panel):
	bl_space_type = "VIEW_3D"
	bl_region_type = "TOOLS"
	#bl_context = "objectmode"
	bl_category = "CGA Shape Grammar"
	bl_label = "Main"
	
	def draw(self, context):
		scene = context.scene
		
		layout = self.layout
		box = layout.box()
		box.row().prop(scene, "ruleFile")
		box.row().operator("object.apply_cga_rule")

class Cga(bpy.types.Operator):
	bl_idname = "object.apply_cga_rule"
	bl_label = "Apply CGA rule"
	bl_options = {"REGISTER", "UNDO"}
	
	collection = bpy.props.CollectionProperty(type=CustomFloatProperty)
	
	def invoke(self, context, event):
		ruleFile = context.scene.ruleFile
		if len(ruleFile)>1 and ruleFile[:2]=="//":
			ruleFile = ruleFile[2:]
		ruleFile = os.path.join(os.path.dirname(bpy.data.filepath), ruleFile)
		if os.path.isfile(ruleFile):
			module,attrs = bcga.apply(ruleFile)
			self.module = module
			self.attrs = attrs
			# new attrs arrived, so clean self.collection items
			self.collection.clear()
			# for each entry in self.attrs create a new item in self.collection
			for attr in self.attrs:
				item = self.collection.add()
				item.value = attr[1].value
				attr[1].guiItem = item
		else:
			self.report({"ERROR"}, "The rule file %s not found" % ruleFile)
		return {"FINISHED"}
	
	def execute(self, context):
		for attr in self.attrs:
			attrName = attr[0]
			attr = attr[1]
			attr.value = getattr(attr.guiItem, "value")
		bcga.apply(self.module)
		return {"FINISHED"}
	
	def draw(self, context):
		layout = self.layout
		if hasattr(self, "attrs"):
			# self.attrs is a list of tuples: (attrName, instanceofAttrClass)
			for attr in self.attrs:
				attrName = attr[0]
				row = self.layout.split()
				row.label(attrName+":")
				row.prop(attr[1].guiItem, "value")


def register():
	bpy.utils.register_module(__name__)

def unregister():
	bpy.utils.unregister_module(__name__)