import math
import bpy
import cga, bcga
from cga.op_comp import front, side, top
from cga import context

normalThreshold = 0.98

class Comp(cga.op_comp.Comp):
	normalThreshold = normalThreshold
	normalThreshold2 = math.sqrt(1-normalThreshold*normalThreshold)
	
	def execute(self):
		operatorDef = self.operatorDef
		state = context.getExecutionState()
		if not state['valid']:
			print("comp", self.compSelector, "invalid state")
		print("executing comp", self.compSelector)
		
		# create a dict from the operatorDef list
		parts = {}
		for part in operatorDef.parts:
			selector = part.value
			parts[part.value] = part
		
		bContext = bpy.context
		
		# active object
		obj = bContext.active_object
		
		# a hack to skip the bottom polygon FIXME
		skipHorizontalPolygon = True
		
		# list of newly created Blender objects and its rule or operator
		components = []
		# iterate till we have something to decompose
		target = True
		while target:
			target = None
			for polygon in obj.data.polygons:
				# is the polygon a target one for the selector
				normal = polygon.normal
				# vertical component of the normal
				nv = math.fabs(normal[2])
				if nv<=self.normalThreshold2:
					# vertical polygon
					if front in parts:
						target = parts[front]
						del parts[front] # a hack FIXME
					elif side in parts:
						target = parts[side]
				elif nv>self.normalThreshold:
					# horizontal polygon
					if top in parts:
						if skipHorizontalPolygon:
							skipHorizontalPolygon = False
						else:
							target = parts[top]
							del parts[top] # a hack FIXME
				if target:
					break
			if target:
				polygon.select = True
				bpy.ops.object.mode_set(mode="EDIT")
				bpy.ops.mesh.separate()
				bpy.ops.object.mode_set(mode="OBJECT")
				# finding the object that has been just separated from the active object
				# it's the one of the two selected objects
				selected = bContext.selected_objects
				separatedObject = selected[0] if selected[1]==obj else selected[1]
				name = str(target)
				separatedObject.name = name
				separatedObject.data.name = name
				# remove selection
				separatedObject.select = False
				components.append((separatedObject, target))
		
		if len(components)>0:
			# select all newly created component objects
			for part in components:
				part[0].select = True
			# perform parenting
			bcga.parent_set()
			
			# now apply the rule for each decomposed Blender object
			for part in components:
				context.pushExecutionState()
				bContext.scene.objects.active = part[0]
				part[1].execute()
				context.popExecutionState()
			# invalidate state
			state['valid'] = False
