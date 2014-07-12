bl_info = {
	"name": "CGA",
	"author": "Vladimir Elistratov <vladimir.elistratov@gmail.com>",
	"version": (0, 0, 0),
	"blender": (2, 7, 0),
	"location": "View 3D > Specials [W-key] > CGA Shape Grammar",
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

class CgaMainPanel(bpy.types.Panel):
	bl_space_type = "VIEW_3D"
	bl_region_type = "TOOLS"
	bl_context = "objectmode"
	bl_category = "CGA Shape Grammar"
	bl_label = "Main"
	
	def draw(self, context):
		scene = context.scene
		
		layout = self.layout
		layout.row().prop(scene, "ruleFile")
		layout.row().operator("object.apply_cga_rule")
		if hasattr(cgaContext, "attrNames"):
			for attrName in cgaContext.attrNames:
				layout.row().prop(scene, attrName)

class Cga(bpy.types.Operator):
	bl_idname = "object.apply_cga_rule"
	bl_label = "Apply CGA rule"
	bl_options = {"REGISTER", "UNDO"}
	
	def execute(self, context):
		ruleFile = context.scene.ruleFile
		if len(ruleFile)>1 and ruleFile[:2]=="//":
			ruleFile = ruleFile[2:]
		ruleFile = os.path.join(os.path.dirname(bpy.data.filepath), ruleFile)
		if os.path.isfile(ruleFile):
			bcga.apply(ruleFile)
		else:
			self.report({"ERROR"}, "The rule file %s not found" % ruleFile)
		return {"FINISHED"}


def register():
	bpy.utils.register_module(__name__)

def unregister():
	bpy.utils.unregister_module(__name__)