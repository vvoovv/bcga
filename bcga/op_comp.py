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
		state = context.getExecutionState()
		if not state['valid']:
			print("comp", self.compSelector, "invalid state")
		
		bm = context.bm
		
		# create a dict from the operatorDef list
		parts = {}
		for part in self.parts:
			selector = part.value
			parts[part.value] = part
		
		# a hack to skip the bottom face FIXME
		skipHorizontalFace = True
		
		# list of face indices and their rule or operator
		components = []
		# create a dictionary of faces with face indices as the dictionary keys
		faces = {}
		for face in bm.faces:
			faces[face.index] = face
		# iterate till we have something to decompose
		target = True
		while target:
			target = None
			for face in faces:
				face = faces[face]
				# is the face a target one for the selector?
				normal = face.normal
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
						if skipHorizontalFace:
							skipHorizontalFace = False
						else:
							target = parts[top]
							del parts[top] # a hack FIXME
				if target:
					del faces[face.index]
					components.append((face, target))
					break
		
		if len(components)>0:
			# now apply the rule for each decomposed Blender object
			for part in components:
				context.pushExecutionState(shape=part[0])
				part[1].execute()
				context.popExecutionState()
			# invalidate state
			state['valid'] = False
