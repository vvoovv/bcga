import bpy, bmesh, mathutils
from pro import context
from pro import x, y
from pro import front, back, left, right, top, bottom, side, all
from pro.op_split import calculateSplit
from .util import rotation_zNormal_xHorizontal, getEndVertex, unityThreshold, zAxis

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

def createRectangle(verts):
    face = context.bm.faces.new(verts)
    return Rectangle(face.loops[0])

def createShape2d(verts):
    face = context.bm.faces.new(verts)
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
        # a dict uvLayer -> instance of bpro.op_texture.Texture
        self.uvLayers = {}
    
    def extrude(self, extrude):
        """
        Args:
            extrude (pro.op_extrude.Extrude): Instance of pro.op_extrude.Extrude
        """
        depth = extrude.depth
        bm = context.bm
        # store the reference to the original face
        originalFace = self.face
        # execute extrude operator
        geom = bmesh.ops.extrude_face_region(bm, geom=(originalFace,))
        # find extruded face
        for extrudedFace in geom["geom"]:
            if isinstance(extrudedFace, bmesh.types.BMFace):
                break
        # perform translation along the extrudedFace normal
        bmesh.ops.translate(bm, verts=extrudedFace.verts, vec=depth*extrudedFace.normal)
        
        # Find a face connecting originalFace and extrudedFace, that contains the original first loop.
        # The normal for the original face has been reversed, so self.firstLoop doesn't contain
        # the original edge anymore 
        # The original first edge:
        edge = self.firstLoop.link_loop_prev.edge
        # loops connected to the first esge
        loops = edge.link_loops
        # find the loop that belong to the face we are looking for (the face connects originalFace and extrudedFace)
        for loop in loops:
            oppositeLoop = loop.link_loop_next.link_loop_next
            _loops = oppositeLoop.link_loops
            if len(_loops)==1 and _loops[0].face==extrudedFace:
                break
        extrudedFirstLoop = _loops[0]
        
        # now we have a 3D shape
        # build a list of 2D shapes (faces) that costitute the 3D shape
        shapes = []
        if extrude.keepOriginal:
            shapes.append(self)
            # index of the first side shape
            sideIndex = 2
        else:
            sideIndex = 1
            context.facesForRemoval.append(self.face)
        constructor = type(self)
        shapes.append(constructor(oppositeLoop.link_loops[0]))
        startLoop = loop
        while True:
            if extrudedFace.normal[2]>unityThreshold:
                # first, consider the special case for the horizontal extrudedFace
                shapes.append(Rectangle(loop))
            else:
                # Find which edge of the edges along the direction of extrusion
                # has the lowest vertex
                # the first edge along the direction of extrusion
                loop1 = loop.link_loop_next
                loop2 = loop1.link_loop_next
                z1 = min(loop1.vert.co[2], loop2.vert.co[2])
                # the second edge along the direction of extrusion
                loop1 = loop
                loop2 = loop1.link_loop_prev
                z2 = min(loop1.vert.co[2], loop2.vert.co[2])
                # Choose the loop belonging to the edge with the lowest vertex
                # as the first loop for the rectangle to be created
                # If z1==z2 (i.e. the rectangle is horizontal)
                # choose the opposite loop as the first loop for the rectangle to be created
                if extrude.alwaysAlongOriginal or z1==z2:
                    _firstLoop = loop
                elif z1<z2:
                    _firstLoop = loop.link_loop_next
                else:
                    _firstLoop = loop.link_loop_prev
                shapes.append(Rectangle(_firstLoop))
            # proceed to the next face connecting originalFace and extrudedFace
            loop = loop.link_loop_next.link_loops[0].link_loop_next
            if loop == startLoop:
                break
        
        # Inherit material from the original shape
        # depending on settings (inheritMaterialAll, inheritMaterialSide, inheritMaterialExtruded).
        # The extruded face in Blender inherits uv-coordinates and material of the original face automatically.
        # So there is no need to process inheritMaterialExtruded.
        # However we still need set UV-coordinates and to copy entries from self.uvLayers for the extruded face
        materialIndex = self.face.material_index
        if extrude.inheritMaterialAll or extrude.inheritMaterialExtruded:
            # extruded shape
            shape = shapes[sideIndex-1]
            for layer in self.uvLayers:
                # No need to call shape.setUV(...) for the extruded shape,
                # since UV-coordinates are copied by Blender automatically
                # No need to set preview texture for the extruded shape.
                # since the preview texture is set automatically by Blender
                shape.addUVlayer(layer, self.uvLayers[layer])
        if extrude.inheritMaterialSide or extrude.inheritMaterialAll:
            numShapes = len(shapes)
            if len(self.uvLayers)>0:
                # inherit uv-coordinates
                for i in range(sideIndex, numShapes):
                    shape = shapes[i]
                    for layer in self.uvLayers:
                        shape.setUV(layer, self.uvLayers[layer])
            # inherit material_index and set preview texture
            for i in range(sideIndex, numShapes):
                shape = shapes[i]
                shape.face.material_index = materialIndex
                context.materialManager.setPreviewTexture(shape, materialIndex)

        # perform some cleanup
        self.clearUVlayers()
        return Shape3d(shapes, extrudedFirstLoop, niche=True if depth<0 else False)

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
        So we have to calculated it explicitly
        """
        loop = self.firstLoop
        v1 = getEndVertex(loop).co - loop.vert.co
        loop = loop.link_loop_next
        v2 = getEndVertex(loop).co - loop.vert.co
        normal = v1.cross(v2)
        normal.normalize()
        return normal
    
    def addUVlayer(self, layer, tex):
        """
        Adds a new entry to self.uvLayers
        
        Args:
            layer (str): UV-layer, a key for self.uvLayers
            tex (bpro.op_texture.Texture): Instance of bpro.op_texture.Texture
        """
        self.uvLayers[layer] = tex
    
    def clearUVlayers(self):
        self.uvLayers.clear()
    
    def setUV(self, layer, tex):
        """
        Assigns uv-coordinates to the shape for the specified uv-layer and adds layer to self.uvLayers
        
        Args:
            layer (str): UV-layer
            tex (bpro.op_texture.Texture): Instance of bpro.op_texture.Texture
        """
        # texture width in the units of global coordinate system
        width = tex.width
        # texture height in the units of global coordinate sytem
        height = tex.height
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
        # add layer to self.uvLayers
        self.addUVlayer(layer, tex)
    
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
    
    def center(self):
        """
        Returns the center of shape in the global coordinate system
        """
        center = None
        firstLoop = self.firstLoop
        # iterate through all loops of the face
        loop = firstLoop
        while True:
            if center:
                center += loop.vert.co
            else:
                center = loop.vert.co
            loop = loop.link_loop_next
            if loop == firstLoop:
                break
        return center/len(self.face.verts)
    
    def delete(self):
        context.facesForRemoval.append(self.face)


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
        
        # a degenerate case, i.e. no cut is needed
        if len(cuts)==1:
            # return immediately
            return cuts
        
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
            v1 = context.vertexRegistry.getVertex(v1.to_tuple())
            v2 = context.vertexRegistry.getVertex(v2.to_tuple())
            verts = (prevVert1, v1, v2, prevVert2) if direction==x else (prevVert2, prevVert1, v1, v2)
            # the element of the list cut with index 1 was reserved for the 2D-shape
            cut[1] = createRectangle(verts)
            prevVert1 = v1
            prevVert2 = v2
        # create a face for the last cut section (cutValue=1)
        verts = (prevVert1, end1, end2, prevVert2) if direction==x else (prevVert2, prevVert1, end1, end2)
        cuts[-1][1] = createRectangle(verts)
        
        context.facesForRemoval.append(self.face)
        
        materialIndex = self.face.material_index
        
        if len(self.uvLayers)>0:
            # Assign uv coordinates for each uvLayer and for each newly cut shape
            # The uv coordinates are inherited from the parent shape
            for layer in self.uvLayers:
                uvLayer = bm.loops.layers.uv[layer]
                
                # origin for the uv space
                origin = firstLoop[uvLayer].uv
                # end point of vector the uv space, oriented along u-axis
                endU = firstLoop.link_loop_next[uvLayer].uv
                # end point of vector the uv space, oriented along v-axis
                endV = firstLoop.link_loop_prev[uvLayer].uv
                # vector in the uv space along u-axis (direction==x) or v-axis (direction==y)
                vec = endU-origin if direction==x else endV-origin
                
                lastCutValue = 0
                for cut in cuts:
                    cutValue = cut[0]
                    shape = cut[1]
                    loops = shape.face.loops
                    if direction == x:
                        loops[0][uvLayer].uv = origin + lastCutValue*vec
                        loops[1][uvLayer].uv = origin + cutValue*vec
                        loops[2][uvLayer].uv = endV + cutValue*vec
                        loops[3][uvLayer].uv = endV + lastCutValue*vec
                    else:
                        loops[0][uvLayer].uv = origin + lastCutValue*vec
                        loops[1][uvLayer].uv = endU + lastCutValue*vec
                        loops[2][uvLayer].uv = endU + cutValue*vec
                        loops[3][uvLayer].uv = origin + cutValue*vec
                    shape.addUVlayer(layer, self.uvLayers[layer])
                    lastCutValue = cutValue
        
        # finally, inherit the material_index from the parent shape and set preview texture
        for cut in cuts:
            cut[1].face.material_index = materialIndex
            context.materialManager.setPreviewTexture(cut[1], materialIndex)
        # perform some cleanup
        self.clearUVlayers()
        return cuts
    
    def setUV(self, layer, tex, offsetX=0, offsetY=0):
        """
        Overloads Shape2d.setUV
        """
        # texture width in the units of global coordinate system
        width = tex.width
        # texture height in the units of global coordinate sytem
        height = tex.height
        uvLayer = context.bm.loops.layers.uv[layer]
        loop = self.firstLoop
        if width==0 or height==0:
            # treat the special case
            loop[uvLayer].uv = (0, 0)
            loop = loop.link_loop_next
            loop[uvLayer].uv = (1, 0)
            loop = loop.link_loop_next
            loop[uvLayer].uv = (1, 1)
            loop = loop.link_loop_next
            loop[uvLayer].uv = (0, 1)
        else:
            size = self.size()
            width = size[0]/width
            height = size[1]/height
            loop[uvLayer].uv = (offsetX, offsetY)
            loop = loop.link_loop_next
            loop[uvLayer].uv = (offsetX+width, offsetY+0)
            loop = loop.link_loop_next
            loop[uvLayer].uv = (offsetX+width, offsetY+height)
            loop = loop.link_loop_next
            loop[uvLayer].uv = (offsetX, offsetY+height)
        # add layer to self.uvLayers
        self.addUVlayer(layer, tex)
    
    def size(self):
        """
        Overloads Shape2d.size
        """
        firstLoop = self.firstLoop
        width = (getEndVertex(firstLoop).co - self.origin).length
        height = (self.origin - firstLoop.link_loop_prev.vert.co).length
        return (width, height)
    
    def extrude2(self, parts, defs):
        from .op_delete import Delete
        materialManager = context.materialManager
        def inheritMaterial(shape, loop1, loop2, bm):
            """A helper function for material inheritance"""
            loops = shape.face.loops
            for layer in self.uvLayers:
                uvLayer = bm.loops.layers.uv[layer]
                uv1 = loop1[uvLayer].uv
                uv2 = loop2[uvLayer].uv
                # shape width
                w = (vert1.co-prevVert1.co).length
                if axis == x:
                    # u-coordinate for vert1 and vert2
                    u = uv1[0] + w
                    loops[0][uvLayer].uv = uv1
                    loops[1][uvLayer].uv = (u, uv1[1])
                    loops[2][uvLayer].uv = (u, uv2[1])
                    loops[3][uvLayer].uv = uv2
                else:
                    # v-coordinate for vert1 and vert2
                    v = uv1[1] + w
                    loops[0][uvLayer].uv = uv1
                    loops[1][uvLayer].uv = uv2
                    loops[2][uvLayer].uv = (uv2[0], v)
                    loops[3][uvLayer].uv = (uv1[0], v)
                shape.addUVlayer(layer, self.uvLayers[layer])
            # inherit material_index and set preview texture
            shape.face.material_index = materialIndex
            materialManager.setPreviewTexture(shape, materialIndex)
            loop1 = loops[1] if axis == x else loops[3]
            loop2 = loops[2] if axis == x else loops[2]
            return loop1, loop2
            
        
        bm = context.bm
        
        axis = defs.axis
        # we consider that x-axis of the shape coordinate system is oriented along the firstLoop
        firstLoop = self.firstLoop
        # calculate the length of the reference edge
        v = (firstLoop if axis==x else firstLoop.link_loop_next).edge.verts
        width = (v[1].co-v[0].co).length
        # initial points for a newly created rectangle 2D-shape
        prevVert1 = firstLoop.vert
        # loop for the prevVert1 is needed to set uv-coordinates
        loop1 = firstLoop
        prevVert2 = firstLoop.link_loop_prev if axis==x else firstLoop.link_loop_next
        # loop for the prevVert2 is needed to set uv-coordinates
        loop2 = prevVert2
        prevVert2 = prevVert2.vert
        height = (prevVert2.co-prevVert1.co).length
        # matrix is a reverse one to the matrix returned by self.getMatrix
        matrix = mathutils.Matrix.Translation(self.origin) * rotation_zNormal_xHorizontal(firstLoop, self.getNormal(), True)
        
        materialIndex = self.face.material_index
        
        # check if need to create cap1
        _cap1 = defs.cap1 if defs.cap1 else defs.cap
        # Use cap1 variable to store vertices for cap number 1.
        # The stuff ([prevVert1] if axis==x else [None, prevVert1]) is needed
        # to ensure that the edge from the original shape will be the first edge in cap1
        cap1 = None if isinstance(_cap1, Delete) else ([prevVert1] if axis==x else [None, prevVert1])
        # check if need to create cap2
        _cap2 = defs.cap2 if defs.cap2 else defs.cap
        # Use cap2 variable to store vertices for cap number 2.
        # The stuff ([prevVert2] if axis==y else [None, prevVert2]) is needed
        # to ensure that the edge from the original shape will be the first edge in cap2
        cap2 = None if isinstance(_cap2, Delete) else ([prevVert2] if axis==y else [None, prevVert2])
        
        shapesWithRule = []
        numParts = len(parts)
        # For symmetric extrusions: check for a middle part if numParts is even and defs.middle is given
        middleIndex = numParts//2 if defs.symmetric and numParts % 2 == 0 and defs.middle else -1
        partIndex = 0
        while partIndex<numParts:
            part = parts[partIndex]
            # coordinate along the reference edge
            coord = part[0]*width
            depth = part[1]
            if axis==x:
                x1 = coord
                x2 = coord
                y1 = 0
                y2 = height
            else:
                x1 = 0
                x2 = height
                y1 = coord
                y2 = coord
            # vert1
            vert1 = matrix*mathutils.Vector((x1, y1, depth))
            vert1 = bm.verts.new(vert1)
            # vert2
            vert2 = matrix*mathutils.Vector((x2, y2, depth))
            vert2 = bm.verts.new(vert2)
            verts = (prevVert1, vert1, vert2, prevVert2) if axis==x else (prevVert1, prevVert2, vert2, vert1)
            shape = createRectangle(verts)
            # inherit material if necessary
            if defs.inheritMaterialAll or defs.inheritMaterialSection:
                loop1, loop2 = inheritMaterial(shape, loop1, loop2, bm)
            # check we have a rule for the shape
            rule = None
            # check from more to less specific rules
            if len(part)==3:
                # we have a specific rule for that section of extrusion
                rule = part[2]
            elif middleIndex == partIndex:
                rule = defs.middle
            elif defs.section:
                rule = defs.section
            if rule:
                shapesWithRule.append((shape, rule))
            if cap1:
                cap1.append(vert1)
            if cap2:
                cap2.append(vert2)
            prevVert1 = vert1
            prevVert2 = vert2
            partIndex += 1
        # create a rectangle shape for the closing section finishing at coord==1 with depth==0
        vert1 = firstLoop.link_loop_next if axis==x else firstLoop.link_loop_prev
        vert2 = (vert1.link_loop_next if axis==x else vert1.link_loop_prev).vert
        vert1 = vert1.vert
        verts = (prevVert1, vert1, vert2, prevVert2) if axis==x else (prevVert1, prevVert2, vert2, vert1)
        shape = createRectangle(verts)
        # inherit material if necessary
        if defs.inheritMaterialAll or defs.inheritMaterialSection:
            inheritMaterial(shape, loop1, loop2, bm)
        # check if we a rule for the closing section
        rule = None
        if defs.symmetric:
            # the rule for the closing section is the same as for the very first section
            part = parts[0]
            if len(part)==3:
                # we have a specific rule for that section of extrusion
                rule = part[2]
            elif defs.section:
                rule = defs.section
        elif defs.last:
            rule = defs.last
        elif defs.section:
            rule = defs.section
        if rule:
            shapesWithRule.append((shape, rule))
        # treat caps
        if cap1:
            # ensure that the edge from the original shape will be the first edge in cap1
            if axis==x:
                cap1.append(vert1)
                cap1.append(cap1[0])
                cap1.reverse()
                cap1.pop()
            else:
                cap1[0] = vert1
            shape = createShape2d(cap1)
            # inherit material if necessary
            if defs.inheritMaterialAll or defs.inheritMaterialCap:
                for layer in self.uvLayers:
                    shape.setUV(layer, self.uvLayers[layer])
                # inherit material_index and set preview texture
                shape.face.material_index = materialIndex
                materialManager.setPreviewTexture(shape, materialIndex)
            if _cap1:
                # _cape1 is the rule for shape
                shapesWithRule.append((shape, _cap1))
        if cap2:
            # ensure that the edge from the original shape will be the first edge in cap2
            if axis==y:
                cap2.append(vert2)
                cap2.append(cap2[0])
                cap2.reverse()
                cap2.pop()
            else:
                cap2[0] = vert2
            shape = createShape2d(cap2)
            # inherit material if necessary
            if defs.inheritMaterialAll or defs.inheritMaterialCap:
                for layer in self.uvLayers:
                    shape.setUV(layer, self.uvLayers[layer])
                # inherit material_index and set preview texture
                shape.face.material_index = materialIndex
                materialManager.setPreviewTexture(shape, materialIndex)
            if _cap2:
                # _cape2 is the rule for shape
                shapesWithRule.append((shape, _cap2))
        
        if not defs.keepOriginal:
            context.facesForRemoval.append(self.face)
            
        return shapesWithRule
    
    def center(self):
        """
        Overloads Shape2d.center
        """
        return (self.origin + self.firstLoop.link_loop_next.link_loop_next.vert.co)/2
                

class Shape3d:
    """
    Z-axis of the 3D-shape coordinate system is oriented along the z-axis of the global coordinate system.
    X-axis of the 3D-shape coordinate system lies in the first face and parallel to the xy-plane of the global coordinate system.
    If the first face is parallel to the xy-plane of the global coordinate system, then
    x-axis of the 3D-shape coordinate system is oriented along the firstLoop.
    """
    
    def __init__(self, shapes, firstLoop, **kwargs):
        """
        Sets a texture for the 2D-shape
        
        Args:
            shapes (list): List of 2D shapes
            firstLoop (BMLoop): The first loop
        
        Kwargs:
            niche (bool): Does the 3D shapes constitues a niche, e.g. as a result of extrude operation with negative depth
        """
        self.niche = False
        # apply kwargs
        for k in kwargs:
            setattr(self, k, kwargs[k])
        # set 2D shapes (faces) that constitute the 3D-shape
        self.shapes = shapes
        self.firstLoop = firstLoop
        # setting the origin of the shape coordinate system
        self.origin = firstLoop.vert.co
        # rotation matrix is calculated on demand
        self.rotationMatrix = None
    
    def decompose(self, parts):
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
                if self.niche:
                    shapeType = top if normal[2]<0 else bottom
                else:
                    shapeType = top if normal[2]>0 else bottom
                isVertical = False
            else:
                if abs(normal[0]) > abs(normal[1]):
                    if self.niche:
                        shapeType = right if normal[0]<0 else left
                    else:
                        shapeType = right if normal[0]>0 else left
                else:
                    shapeType = front if normal[1]<0 else back
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
    
    def delete(self):
        for shape in self.shapes:
            shape.delete()