import mathutils

from pro import context

xAxis = mathutils.Vector((1, 0, 0))
yAxis = mathutils.Vector((0, 1, 0))
zAxis = mathutils.Vector((0, 0, 1))

zero = 0.000001

unityThreshold = 0.999

def rotation_zNormal_xHorizontal(firstLoop, normal=None, reverse=False):
    """
    Returns a rotation matrix that performs the following rotation.
    Z-axis of the 2D-shape coordinate sytem (aligned with the shape normal)
    becomes aligned with the z-axis of the global coordinate system.
    X-axis of the shape coordinate system (parallel to the xy plane of the global coordinate system)
    becomes aligned with the x-axis of the global coordinate system
    If the shape is parallel to the xy-plane
    (i.e. the shape normal is aligned along z-axis of the global coordinate system),
    then x-axis of the shape coordinate system is aligned along the firstEdge
    
    Args:
        firstLoop (bmesh.types.BMLoop): The first loop of a face
        normal (mathutils.Vector): A normal to the face, since it may not be presented in firstLoop
        reverse (bool): If True, the reversed rotation matrix is returned
    """
    if not normal:
        normal = firstLoop.face.normal
    # compose a normalized vector along firstLoop
    firstLoopVector = getEndVertex(firstLoop).co - firstLoop.vert.co
    firstLoopVector.normalize()
    # create a rotation matrix instance with default values
    rotationMatrix = mathutils.Matrix()
    
    # First consider special cases:
    # when normal is aligned along z-axis of the global coordinate system
    if normal[2]>unityThreshold:
        # Normal is aligned along the positive direction of z-axis of the global coordinate system.
        # The rotation axis is aligned along the negative direction of z-axis of the global coordinate system.
        
        # cosine and sine of the angle between xAxis and firstEdge
        cos = firstLoopVector[0]
        sin = firstLoopVector[1]
        if reverse:
            sin = -sin
        # rotation matrix from firstEdge to xAxis with -zAxis as the rotation axis
        rotationMatrix[0][0:2] = cos, sin
        rotationMatrix[1][0:2] = -sin, cos
    elif normal[2]<-unityThreshold:
        # Normal is aligned along the negative direction of z-axis of the global coordinate system
        # The rotation axis lies in the xy plane of the global coordinate system.
        # The rotation axis is the bisecting vector between xAxis and firstEdge
        # The rotation angle is equal to 180 degrees
        axis = firstLoopVector + xAxis
        axis.normalize()
        
        rotationMatrix[0][0] = 2*axis[0]*axis[0] - 1
        rotationMatrix[0][1] = 2*axis[0]*axis[1]
        
        rotationMatrix[1][0] = 2*axis[1]*axis[0]
        rotationMatrix[1][1] = 2*axis[1]*axis[1] - 1
        
        rotationMatrix[2][2] = -1
    else:
        # Now the general case
        # Find intersection of the shape's plane and xy-plane of the global coordinate system.
        # It gives us the direction of the x-axis of the shape coordinate system.
        shapeX = zAxis.cross(normal)
        shapeX.normalize()
        # The rotation axis is the intersection of two bisecting planes
        # 1) Find the normal to the bisecting plane between zAxis and normal to the shape
        bisectPlaneNormal1 = shapeX.cross(zAxis + normal)
        # 2) Find the normal to the bisecting plane between xAxis and shapeX
        if shapeX[0]<-unityThreshold:
            # the special case shapeX==-xAxis
            bisectPlaneNormal2 = xAxis
        else:
            bisectPlaneNormal2 = zAxis.cross(xAxis + shapeX)
        # Intersection of the two bisecting planes gives us the direction of the rotation axis:
        axis = bisectPlaneNormal1.cross(bisectPlaneNormal2)
        axis.normalize()
        
        # Find the rotation angle
        # First, find the projection of the z-axis and the normal to the shape plane onto
        # the plane perpendicular to the rotation axis
        p1 = axis.cross(zAxis.cross(axis))
        p1.normalize()
        p2 = axis.cross(normal.cross(axis))
        p2.normalize()
        # The rotation angle is the angle between p1 and p2
        # Calculate sine and cosine of the rotation angle
        cos = p1.dot(p2)
        sin = p1.cross(p2).length
        # The last step: check if the axis is pointing in the correct direction,
        # otherwise reverse its direction
        # So we perform rotation that rotates normal to zAxis and p2 to p1:
        if axis.dot(p2.cross(p1))<0:
            axis = -axis
        # Now we are ready to compose the rotation matrix,
        # that describes our rotation normal->zAxis, p2->p1
        _cos = 1 - cos
        if reverse:
            sin = -sin
        rotationMatrix[0][0] = cos + axis[0]*axis[0]*_cos
        rotationMatrix[0][1] = axis[0]*axis[1]*_cos - axis[2]*sin
        rotationMatrix[0][2] = axis[0]*axis[2]*_cos + axis[1]*sin
        
        rotationMatrix[1][0] = axis[1]*axis[0]*_cos + axis[2]*sin
        rotationMatrix[1][1] = cos + axis[1]*axis[1]*_cos
        rotationMatrix[1][2] = axis[1]*axis[2]*_cos - axis[0]*sin
        
        rotationMatrix[2][0] = axis[2]*axis[0]*_cos - axis[1]*sin
        rotationMatrix[2][1] = axis[2]*axis[1]*_cos + axis[0]*sin
        rotationMatrix[2][2] = cos + axis[2]*axis[2]*_cos
    
    return rotationMatrix
    
    
def getEndVertex(loop):
    """
    Returns the end vertex for the loop
    """
    return loop.link_loop_next.vert


class VertexRegistry:
    """A helper class to ensure vertex uniqueness"""
    def __init__(self):
        self.verts = {}
    
    def getVertex(self, coords):
        if coords in self.verts:
            vert = self.verts[coords]
        else:
            vert = context.bm.verts.new(coords)
            self.verts[coords] = vert
        return vert