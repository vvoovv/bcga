import bpy
import cga, bcga
from cga import context
from cga.op_split import calculateSplit

class Split(cga.op_split.Split):
	def execute(self):
		operatorDef = self.operatorDef
		# splitting a rectange
		bContext = bpy.context
		# active object
		obj = bContext.active_object
		mesh = obj.data
		vertices = mesh.vertices
		# finding horizontal and vertical edges
		horizontalEdges = []
		verticalEdges = []
		for edge in mesh.edges:
			v1 = vertices[edge.vertices[0]].co
			v2 = vertices[edge.vertices[1]].co
			if v1[2]==v2[2]: # z coordinates are the same
				horizontalEdges.append(edge)
			else:
				origin,end = (v1,v2) if v2[2]>v1[2] else (v2,v1)
				verticalEdges.append((origin,end))
		# calculate scope size (i.e. edge length) along the direction of split
		edge = verticalEdges[0] if self.direction == cga.y else horizontalEdges[0]
		scopeSize = (edge[1]-edge[0]).length
		cuts = calculateSplit(operatorDef, scopeSize)
		if self.direction == cga.y:
			# vertical split
			# vertical edges
			e1 = verticalEdges[0]
			e2 = verticalEdges[1]
			# initial lower points for a newly cut rectangle
			lowerPoint1 = e1[0]
			lowerPoint2 = e2[0]
			for cut in cuts:
				cutValue = cut[0]
				v1 = e1[0] + cutValue*(e1[1]-e1[0])
				v2 = e2[0] + cutValue*(e2[1]-e2[0])
				print(cut[1])
				self.createPolygon(obj, (lowerPoint2, v2, v1, lowerPoint1), str(cut[1]))
				lowerPoint1 = v1
				lowerPoint2 = v2
		# remove all vertices of the active object, but keep the active object with empty mesh for parenting
		bpy.ops.object.mode_set(mode="EDIT")
		bpy.ops.mesh.select_all(action="SELECT")
		bpy.ops.mesh.delete()
		bpy.ops.object.mode_set(mode="OBJECT")
		bcga.parent_set()
		super().execute()
	
	def createPolygon(self, parentObj, vertices, name):
		mesh = bpy.data.meshes.new(name)
		mesh.from_pydata(vertices, [], ((0,1,2,3),))
		obj = bpy.data.objects.new(name, mesh)
		obj.location = parentObj.location
		bpy.context.scene.objects.link(obj)
		obj.select = True
		mesh.update()
