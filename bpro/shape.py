import bpy, bmesh, mathutils
from pro import context
from pro import x, y, z
from pro import front, back, left, right, top, bottom, side, all
from pro.op_split import calculateSplit
from .utils import rotation_zNormal_xHorizontal, getEndVertex, verticalNormalThreshold, zAxis

# normal threshold for the Shape3d.comp method to classify if the face is horizontal or vertical
horizontalFaceThreshold = 0.70711 # math.sqrt(0.5)


def getInitialShape(bm):
    """
    Get initial shape out of bmesh
    """
    face = bm.faces[0]
    # check where the face normal is pointing and reverse it, if necessary
    if face.normal[2]<0:
        bmesh.ops.reverse_faces(bm, faces=(face,))
        
    return Shape2d(face.loops[0])


class Shape2d:
    """
    A base class for all 2D shapes
    """
    def __init__(self, firstLoop):
        self.face = firstLoop.face
        self.firstLoop = firstLoop
        # set the origin of the shape coordinate system
        self.origin = firstLoop.vert.co
        # the transformation matrix from the global coordinate system to the shape coordinate system
        self.matrix = None
        self.uvLayers = set()
    
    def extrude(self, depth):
        bm = context.bm
        # store the reference to the original face
        originalFace = self.face
        # execute extrude operator
        geom = bmesh.ops.extrude_face_region(bm, geom=(originalFace,))
        # find extruded face
        for extrudedFace in geom["geom"]:
            if isinstance(extrudedFace, bmesh.types.BMFace):
                break
        # get extruded vertices
        #verts = [v for v in geom["geom"] if isinstance(v, bmesh.types.BMVert)]
        # perform translation along the extrudedFace normal
        bmesh.ops.translate(bm, verts=extrudedFace.verts, vec=depth*extrudedFace.normal)
        
        # find a face connecting originalFace and extrudedFace, that contains the first edge
        # the first edge:
        edge = self.firstLoop.edge
        # loops connected to the first esge
        loops = edge.link_loops
        # find the loop that belong to the face we are looking for (the face connects originalFace and extrudedFace)
        for loop in loops:
            oppositeLoop = loop.link_loop_next.link_loop_next
            oppositeEdgeFaces = oppositeLoop.edge.link_faces
            if oppositeEdgeFaces[0]==extrudedFace or oppositeEdgeFaces[1]==extrudedFace:
                break
        
        # now we have a 3D shape
        # build a list of 2D shapes (faces) that costitute the 3D shape
        shapes = [self, Shape2d(oppositeLoop.link_loops[0])]
        firstLoop = loop
        if extrudedFace.normal[2]>verticalNormalThreshold:
            # first, consider the special case for the horizontal extrudedFace
            while True:
                shapes.append(Rectangle(loop))
                # proceed to the next face connecting originalFace and extrudedFace
                loop = loop.link_loop_next.link_loops[0].link_loop_next
                if loop == firstLoop:
                    break
        else:
            # now, consider the general case
            pass
        
        return Shape3d(shapes, self.firstLoop)

    def getMatrix(self):
        """
        Returns the transformation matrix from the global coordinate system to the shape coordinate system
        """
        if not self.matrix:
            # translationMatrix is inversed translation matrix from the origin of the global coordinate system to the shape origin
            translationMatrix = mathutils.Matrix.Translation(-self.origin)
            # inversed rotation matrix:
            rotationMatrix = rotation_zNormal_xHorizontal(self.firstLoop, self.getNormal())
            # remember inversed(TRS) = inversed(S)*inversed(R)*inversed(T), so in our case:
            self.matrix = rotationMatrix*translationMatrix
        return self.matrix
    
    def getNormal(self):
        """
        Returns the normal to the shape's face.
        A newly created face (instance of BMFace) has a zero normal
        So we have to calculated explicitly
        """
        loop = self.firstLoop
        v1 = getEndVertex(loop).co - loop.vert.co
        loop = loop.link_loop_next
        v2 = getEndVertex(loop).co - loop.vert.co
        normal = v1.cross(v2)
        normal.normalize()
        return normal
    
    def addUVlayer(self, layer):
        self.uvLayers.add(layer)
    
    def clearUVlayers(self):
        self.uvLayers.clear()
    
    def setUV(self, layer, width, height):
        """
        Assigns uv-coordinates to the shape for the specified uv-layer
        
        Args:
          layer: uv-layer as a string
          width: texture width in the units of global coordinate system
          height: texture height in the units of global coordinate sytem
        """
        uvLayer = context.bm.loops.layers.uv[layer]
        # getting the transformation matrix from the global coordinate system to the shape coordinate system
        matrix = self.getMatrix()
        firstLoop = self.firstLoop
        
        if width==0 or height==0:
            # in this case width and height are taken from the shape size
            width, height = self.size()
        # iterate through all loops of the face
        loop = firstLoop
        while True:
            uv = (matrix*loop.vert.co)[:2]
            # assign uv
            loop[uvLayer].uv = (uv[0]/width, uv[1]/height)
            loop = loop.link_loop_next
            if loop == firstLoop:
                break
    
    def size(self):
        """
        Returns the size of the shape bbox in the shape coordinate system
        """
        # getting the transformation matrix from the global coordinate system to the shape coordinate system
        matrix = self.getMatrix()
        firstLoop = self.firstLoop
        # a list of u-coordinates
        uCoords = []
        # a list of v-coordinates
        vCoords = []
        # iterate through all loops of the face
        loop = firstLoop
        while True:
            uv = matrix*loop.vert.co
            uCoords.append(uv[0])
            vCoords.append(uv[1])
            loop = loop.link_loop_next
            if loop == firstLoop:
                break
        return (max(uCoords)-min(uCoords), max(vCoords)-min(vCoords))


class Rectangle(Shape2d):
    
    def __init__(self, firstLoop):
        super().__init__(firstLoop)
    
    def split(self, direction, parts):
        """
        Returns a list of lists (cutValue between 0 and 1, cutShape, ruleForTheCutShape)
        """
        # we consider that x-axis of the shape coordinate system is oriented along the firstLoop
        firstLoop = self.firstLoop
        
        # referenceLoop is oriented along the positive direction
        referenceLoop = firstLoop if direction==x else firstLoop.link_loop_next
        # vertices of the referenceLoop
        v = referenceLoop.edge.verts
        cuts = calculateSplit(parts, (v[1].co-v[0].co).length)
        
        bm = context.bm
        
        # the loop opposite to referenceLoop
        oppositeLoop = referenceLoop.link_loop_next.link_loop_next
        
        origin1 = referenceLoop.vert
        origin2 = getEndVertex(oppositeLoop)
        
        end1 = getEndVertex(referenceLoop)
        end2 = oppositeLoop.vert
        
        vec1 = end1.co - origin1.co
        vec2 = end2.co - origin2.co
        
        # initial points for a newly cut rectangle 2D-shape
        prevVert1 = origin1
        prevVert2 = origin2
        # the last cut section cuts[-1] is treated separately
        for cutIndex in range(len(cuts)-1):
            cut = cuts[cutIndex]
            cutValue = cut[0]
            v1 = origin1.co + cutValue*vec1
            v2 = origin2.co + cutValue*vec2
            v1 = bm.verts.new(v1)
            v2 = bm.verts.new(v2)
            verts = (prevVert1, v1, v2, prevVert2) if direction==x else (prevVert2, prevVert1, v1, v2)
            # the element of the list cut with index 1 was reserved for the 2D-shape
            cut[1] = self.createSplitShape(verts)
            prevVert1 = v1
            prevVert2 = v2
        # create a face for the last cut section (cutValue=1)
        verts = (prevVert1, end1, end2, prevVert2) if direction==x else (prevVert2, prevVert1, end1, end2)
        cuts[-1][1] = self.createSplitShape(verts)
        
        context.facesForRemoval.append(self.face)
        
        materialIndex = self.face.material_index
        
        if len(self.uvLayers)>0:
            # blenderTexture is needed to set preview texture
            blenderTexture = bpy.context.object.data.materials[materialIndex].texture_slots[0].texture
            # Assign uv coordinates for each uvLayer and for each newly cut shape
            # The uv coordinates are inherited from the parent shape
            for layer in self.uvLayers:
                uv_layer = bm.loops.layers.uv[layer]
                
                # origin for the uv space
                origin = firstLoop[uv_layer].uv
                # end point of vector the uv space, oriented along u-axis
                endU = firstLoop.link_loop_next[uv_layer].uv
                # end point of vector the uv space, oriented along v-axis
                endV = firstLoop.link_loop_prev[uv_layer].uv
                # vector in the uv space along u-axis (direction==x) or v-axis (direction==y)
                vec = endU-origin if direction==x else endV-origin
                
                lastCutValue = 0
                for cut in cuts:
                    cutValue = cut[0]
                    shape = cut[1]
                    loops = shape.face.loops
                    if direction == x:
                        loops[0][uv_layer].uv = origin + lastCutValue*vec
                        loops[1][uv_layer].uv = origin + cutValue*vec
                        loops[2][uv_layer].uv = endV + cutValue*vec
                        loops[3][uv_layer].uv = endV + lastCutValue*vec
                    else:
                        loops[0][uv_layer].uv = origin + lastCutValue*vec
                        loops[1][uv_layer].uv = endU + lastCutValue*vec
                        loops[2][uv_layer].uv = endU + cutValue*vec
                        loops[3][uv_layer].uv = origin + cutValue*vec
                    shape.addUVlayer(layer)
                    lastCutValue = cutValue
            # set preview texture for each newly cut shape
            for cut in cuts:
                cut[1].face[bm.faces.layers.tex.active].image = blenderTexture.image
        
        # finally, inherit the material_index from the parent shape
        for cut in cuts:
            cut[1].face.material_index = materialIndex
        return cuts
    
    def createSplitShape(self, verts):
        bm = context.bm
        face = bm.faces.new(verts)
        return Rectangle(face.loops[0])
    
    def setUV(self, layer, width, height):
        """
        Overloads Shape2d.setUV
        """
        uvLayer = context.bm.loops.layers.uv[layer]
        loops = self.face.loops
        if width==0 or height==0:
            # treat the special case
            loops[0][uvLayer].uv = (0, 0)
            loops[1][uvLayer].uv = (1, 0)
            loops[2][uvLayer].uv = (1, 1)
            loops[3][uvLayer].uv = (0, 1)
        else:
            size = self.size()
            width = size[0]/width
            height = size[1]/height
            loops[0][uvLayer].uv = (0, 0)
            loops[1][uvLayer].uv = (width, 0)
            loops[2][uvLayer].uv = (width, height)
            loops[3][uvLayer].uv = (0, height)
    
    def size(self):
        """
        Overloads Shape2d.size
        """
        firstLoop = self.firstLoop
        width = (getEndVertex(firstLoop).co - self.origin).length
        height = (self.origin - firstLoop.link_loop_prev.vert.co).length
        return (width, height)


class Shape3d:
    """
    Z-axis of the 3D-shape coordinate system is oriented along the z-axis of the global coordinate system.
    X-axis of the 3D-shape coordinate system lies in the first face and parallel to the xy-plane of the global coordinate system.
    If the first face is parallel to the xy-plane of the global coordinate system, then
    x-axis of the 3D-shape coordinate system is oriented along the firstLoop.
    """
    
    def __init__(self, shapes, firstLoop):
        # set 2D shapes (faces) that constitute the 3D-shape
        self.shapes = shapes
        self.firstLoop = firstLoop
        # setting the origin of the shape coordinate system
        self.origin = firstLoop.vert.co
        # rotation matrix is calculated on demand
        self.rotationMatrix = None
    
    def comp(self, parts):
        """
        Returns a dictionary with a comp-selector as the key and a list of 2D-shapes as the related value
        """
        result = {}
        rotationMatrix = self.getRotationMatrix()
        for shape in self.shapes:
            # get normal in the 3D-shape coordinate system
            normal = rotationMatrix * shape.face.normal
            # classify the 2D-shape
            if abs(normal[2]) > horizontalFaceThreshold:
                # the 2D-shape is horizontal
                shapeType = top if normal[2]>0 else bottom
                isVertical = False
            else:
                if abs(normal[0]) > abs(normal[1]):
                    shapeType = front if normal[0]>0 else back
                else:
                    shapeType = right if normal[1]>0 else left
                isVertical = True
            
            if not shapeType in parts:
                if side in parts and isVertical:
                    shapeType = side
                elif all in parts:
                    shapeType = all
                else:
                    shapeType = None
            
            if shapeType:
                if not shapeType in result:
                    result[shapeType] = []
                result[shapeType].append(shape)
        return result
    
    def getRotationMatrix(self):
        if not self.rotationMatrix:
            self.rotationMatrix = rotation_zNormal_xHorizontal(self.firstLoop, zAxis)
        return self.rotationMatrix