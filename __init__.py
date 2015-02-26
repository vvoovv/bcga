bl_info = {
	"name": "Prokitektura",
	"author": "Vladimir Elistratov <vladimir.elistratov@gmail.com>",
	"version": (0, 0, 0),
	"blender": (2, 7, 3),
	"location": "View3D > Tool Shelf",
	"description": "Prokitektura implementation for Blender",
	"warning": "",
	"wiki_url": "https://github.com/prokitektura/prokitektura-blender/wiki/",
	"tracker_url": "https://github.com/prokitektura/prokitektura-blender/issues",
	"support": "COMMUNITY",
	"category": "Prokitektura",
}

import sys, os, math
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

from bpro.bl_util import create_rectangle, align_view

def getRuleFile(ruleFile, operator):
	"""
	Returns full path to a rule file or None if it does not exist.
	"""
	if len(ruleFile)>1 and ruleFile[:2]=="//":
		ruleFile = ruleFile[2:]
	ruleFile = os.path.join(os.path.dirname(bpy.data.filepath), ruleFile)
	if not os.path.isfile(ruleFile):
		operator.report({"ERROR"}, "The rule file %s not found" % ruleFile)
		ruleFile = None
	return ruleFile
	

bpy.types.Scene.ruleFile = bpy.props.StringProperty(
	name = "Rule file",
	description = "Path to a rule file",
	subtype = "FILE_PATH"
)

bpy.types.Scene.bakingRuleFile = bpy.props.StringProperty(
	name = "Low poly rule file",
	description = "Path to a rule file for a low poly model",
	subtype = "FILE_PATH"
)

class CustomFloatProperty(bpy.types.PropertyGroup):
	"""A bpy.types.PropertyGroup descendant for bpy.props.CollectionProperty"""
	value = bpy.props.FloatProperty(name="")

class CustomColorProperty(bpy.types.PropertyGroup):
	"""A bpy.types.PropertyGroup descendant for bpy.props.CollectionProperty"""
	value = bpy.props.FloatVectorProperty(name="", subtype='COLOR', min=0.0, max=1.0)

class ProMainPanel(bpy.types.Panel):
	bl_label = "Main"
	bl_space_type = "VIEW_3D"
	bl_region_type = "TOOLS"
	#bl_context = "objectmode"
	bl_category = "Prokitektura"
	
	def draw(self, context):
		scene = context.scene
		layout = self.layout
		layout.row().operator_menu_enum("object.footprint_set", "size", text="Footprint")
		layout.separator()
		layout.row().prop(scene, "ruleFile")
		layout.row().operator("object.apply_pro_rule")


class ObjectPanel(bpy.types.Panel):
	bl_label = "Baking"
	bl_space_type = "VIEW_3D"
	bl_region_type = "TOOLS"
	bl_category = "Prokitektura"
	bl_options = {"DEFAULT_CLOSED"}
	
	def draw(self, context):
		scene = context.scene
		layout = self.layout
		layout.row().prop(scene, "bakingRuleFile")
		self.layout.operator("object.bake_pro_model")


class Pro(bpy.types.Operator):
	bl_idname = "object.apply_pro_rule"
	bl_label = "Apply Prokitektura rule"
	bl_options = {"REGISTER", "UNDO"}
	
	collectionFloat = bpy.props.CollectionProperty(type=CustomFloatProperty)
	collectionColor = bpy.props.CollectionProperty(type=CustomColorProperty)
	
	def invoke(self, context, event):
		proContext.blenderContext = context
		ruleFile = getRuleFile(context.scene.ruleFile, self)
		if ruleFile:
			# append the directory of the ruleFile to sys.path
			ruleFileDirectory = os.path.dirname(os.path.realpath(os.path.expanduser(ruleFile)))
			if ruleFileDirectory not in sys.path:
				sys.path.append(ruleFileDirectory)

			module,params = bpro.apply(ruleFile)
			
			align_view(context.object)
			
			self.module = module
			self.params = params
			# new params arrived, so clean all collections
			self.collectionFloat.clear()
			self.collectionColor.clear()
			paramCounter = 0
			# for each entry in self.params create a new item in self.collection
			for param in self.params:
				param = param[1]
				if isinstance(param, ParamFloat):
					collectionItem = self.collectionFloat.add()
				elif isinstance(param, ParamColor):
					collectionItem = self.collectionColor.add()
				collectionItem.value = param.getValue()
				param.collectionItem = collectionItem
				paramCounter += 1
				if paramCounter==9:break
		return {"FINISHED"}
	
	def execute(self, context):
		proContext.blenderContext = context
		paramCounter = 0
		for param in self.params:
			param = param[1]
			param.setValue(getattr(param.collectionItem, "value"))
			paramCounter += 1
			if paramCounter==9:break
		bpro.apply(self.module)
		
		align_view(context.object)
		
		return {"FINISHED"}
	
	def draw(self, context):
		layout = self.layout
		if hasattr(self, "params"):
			paramCounter = 0
			# self.params is a list of tuples: (paramName, instanceofParamClass)
			for param in self.params:
				paramName = param[0]
				row = layout.split()
				row.label(paramName+":")
				row.prop(param[1].collectionItem, "value")
				paramCounter += 1
				if paramCounter==9:break


class Bake(bpy.types.Operator):
	bl_idname = "object.bake_pro_model"
	bl_label = "Bake"
	bl_options = {"REGISTER", "UNDO"}
	
	def execute(self, context):
		proContext.blenderContext = context
		bpy.ops.object.select_all(action="DESELECT")
		# remember the original object, it will be used for low poly model
		lowPolyObject = context.object
		lowPolyObject.select = True
		bpy.ops.object.duplicate()
		highPolyObject = context.object
		# high poly model
		ruleFile = getRuleFile(context.scene.ruleFile, self)
		if ruleFile:
			highPolyParams = bpro.apply(ruleFile)[1]
			# convert highPolyParams to a dict paramName->instanceofParamClass
			highPolyParams = dict(highPolyParams)
			
			# low poly model
			context.scene.objects.active = lowPolyObject
			ruleFile = getRuleFile(context.scene.bakingRuleFile, self)
			if ruleFile:
				name = lowPolyObject.name
				module = bpro.getModule(ruleFile)
				lowPolyParams = bpro.getParams(module)
				# Apply highPolyParams to lowPolyParams
				# Normally lowPolyParams is a subset of highPolyParams
				for paramName,param in lowPolyParams:
					if paramName in highPolyParams:
						param.setValue(highPolyParams[paramName].getValue())
				bpro.apply(module)
				# unwrap the low poly model
				bpy.ops.object.mode_set(mode="EDIT")
				bpy.ops.mesh.select_all(action="SELECT")
				bpy.ops.uv.smart_project()
				# prepare settings for baking
				bpy.ops.object.mode_set(mode="OBJECT")
				highPolyObject.select = True
				bpy.context.scene.render.bake_type = "TEXTURE"
				bpy.context.scene.render.use_bake_selected_to_active = True
				# create a new image with default settings for baking
				image = bpy.data.images.new(name=name, width=512, height=512)
				# assign the image to each uv_face
				for uv_face in lowPolyObject.data.uv_textures.active.data:
					uv_face.image = image
				# finally perform baking
				bpy.ops.object.bake_image()
				# delete the high poly object and its mesh
				context.scene.objects.active = highPolyObject
				mesh = highPolyObject.data
				bpy.ops.object.delete()
				bpy.data.meshes.remove(mesh)
				context.scene.objects.active = lowPolyObject
				# assign the baked texture to the low poly object
				blenderTexture = bpy.data.textures.new(name, type = "IMAGE")
				blenderTexture.image = image
				blenderTexture.use_alpha = True
				material = bpy.data.materials.new(name)
				textureSlot = material.texture_slots.add()
				textureSlot.texture = blenderTexture
				textureSlot.texture_coords = "UV"
				textureSlot.uv_layer = "prokitektura"
				lowPolyObject.data.materials.append(material)
		return {"FINISHED"}


class FootprintSet(bpy.types.Operator):
	bl_idname = "object.footprint_set"
	bl_label = "Prokitektura footprint"
	bl_description = "Set a building footprint for Prokitektura"
	bl_options = {"REGISTER", "UNDO"}
	
	size = bpy.props.EnumProperty(
		items = [
			("35x15", "rectangle 35x15", "35x15"),
			("20x10", "rectangle 20x10", "20x10"),
			("10x10", "rectangle 10x10", "10x10")
		]
	)
	
	def execute(self, context):
		lightOffset = 20
		lightHeight = 20
		scene = context.scene
		# delete active object if it is a mesh
		active = context.active_object
		if active and active.type=="MESH":
			bpy.ops.object.delete()
		# getting width and height of the footprint
		w, h = [float(i) for i in self.size.split("x")]
		# add lights
		rx = math.atan((h+lightOffset)/lightHeight)
		rz = math.atan((w+lightOffset)/(h+lightOffset))
		def lamp_add(x, y, rx, rz):
			bpy.ops.object.lamp_add(
				type="SUN",
				location=((x,y,lightHeight)),
				rotation=(rx, 0, rz)
			)
			context.active_object.data.energy = 0.5
		lamp_add(w+lightOffset, h+lightOffset, -rx, -rz)
		lamp_add(-w-lightOffset, h+lightOffset, -rx, rz)
		lamp_add(-w-lightOffset, -h-lightOffset, rx, -rz)
		lamp_add(w+lightOffset, -h-lightOffset, rx, rz)
		
		create_rectangle(context, w, h)
		
		return {"FINISHED"}


def register():
	bpy.utils.register_module(__name__)

def unregister():
	bpy.utils.unregister_module(__name__)