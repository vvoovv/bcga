bl_info = {
	"name": "CGA",
	"author": "Vladimir Elistratov <vladimir.elistratov@gmail.com>",
	"version": (0, 0, 0),
	"blender": (2, 7, 0),
	#"location": "File > Import > OpenStreetMap (.osm)",
	"description": "CGA implementation for Blender",
	"warning": "",
	"wiki_url": "https://github.com/vvoovv/blender-geo/wiki/Import-OpenStreetMap-(.osm)",
	"tracker_url": "https://github.com/vvoovv/blender-geo/issues",
	"support": "COMMUNITY",
	"category": "CGA",
}

import sys, os
for path in sys.path:
	if "bcga" in path:
		path = None
		break
if path:
	# we need to add path to cbga package
	sys.path.append(os.path.dirname(__file__))

import bpy

import bcga

class Cga(bpy.types.Operator):
	bl_idname = "object.apply_cga_rule"
	bl_label = "Apply CGA rule"
	bl_options = {"REGISTER", "UNDO"}
	
	def execute(self, context):
		bcga.apply("D:/projects/blender/py-cga/examples/simple01.py")
		return {"FINISHED"}

def register():
	bpy.utils.register_class(Cga)

def unregister():
	bpy.utils.unregister_class(Cga)