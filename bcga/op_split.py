import bpy
import cga, bcga
from cga import context
from cga.op_split import calculateSplit

class Split(cga.op_split.Split):
	def execute(self):
		state = context.getExecutionState()
		if not state['valid']:
			print("split", self.direction, "invalid state")
		
		bm = context.bm
		self.bm = bm
		# getting current face
		face = state['shape']
		
		# splitting the rectange
		# finding horizontal and vertical edges
		horizontalEdges = []
		verticalEdges = []
		for edge in face.edges:
			vert1 = edge.verts[0]
			vert2 = edge.verts[1]
			v1 = vert1.co
			v2 = vert2.co
			if v1[2]==v2[2]: # z coordinates are the same
				origin,end = (vert1, vert2)
				horizontalEdges.append((origin,end))
			else:
				origin,end = (vert1,vert2) if v2[2]>v1[2] else (vert2,vert1)
				verticalEdges.append((origin,end))
		# calculate scope size (i.e. edge length) along the direction of split
		edge = verticalEdges[0] if self.direction == cga.y else horizontalEdges[0]
		scopeSize = (edge[1].co-edge[0].co).length
		cuts = calculateSplit(self.parts, scopeSize)
		if self.direction == cga.y:
			# vertical split
			e1 = verticalEdges[0]
			e2 = verticalEdges[1]
		elif self.direction == cga.x:
			# horizontal split
			e1 = horizontalEdges[0]
			e2 = horizontalEdges[1]
			# check if e1 and e2 are pointing in the same direction
			if (e1[1].co-e1[0].co).dot(e2[1].co-e2[0].co)<0:
				# change origin and end
				e2 = (e2[1], e2[0])
		# initial points for a newly cut rectangle
		prevPoint1 = e1[0]
		prevPoint2 = e2[0]
		# the last cut section cuts[-1] is treated separately
		for cutIndex in range(len(cuts)-1):
			cut = cuts[cutIndex]
			cutValue = cut[0]
			v1 = e1[0].co + cutValue*(e1[1].co-e1[0].co)
			v2 = e2[0].co + cutValue*(e2[1].co-e2[0].co)
			v1 = bm.verts.new(v1)
			v2 = bm.verts.new(v2)
			# keep the newly cut object in cut[0] 
			cut[0] = self.createFace((prevPoint2, v2, v1, prevPoint1))
			prevPoint1 = v1
			prevPoint2 = v2
		# create a face for the last cut section (cutValue=1)
		cuts[-1][0] = self.createFace((prevPoint2, e2[1], e1[1], prevPoint1))
		
		context.facesForRemoval.append(face)
		
		# now apply the rule for each cut
		for splitIndex,cut in enumerate(cuts):
			context.pushExecutionState(shape=cut[0])
			# inject splitIndex to the context
			context.splitIndex = splitIndex
			cut[1].execute()
			context.popExecutionState()
		if hasattr(context, "splitIndex"):
			delattr(context, "splitIndex")
		# invalidate state
		state['valid'] = False
	
	def createFace(self, verts):
		return self.bm.faces.new(verts)
