import bpy, bmesh
from .util import zero
newObjectName = "Prokitektura"

def create_rectangle(blenderContext, sizeX, sizeY):
    sizeX /= 2
    sizeY /= 2
    if blenderContext.object:
        bpy.ops.object.select_all(action="DESELECT")
    scene = blenderContext.scene
    mesh = bpy.data.meshes.new(newObjectName)
    mesh.from_pydata(
        ((-sizeX,-sizeY,0), (sizeX,-sizeY,0), (sizeX,sizeY,0), (-sizeX,sizeY,0)), [], ((0,1,2,3),)
    )
    obj = bpy.data.objects.new(newObjectName, mesh)
    obj.location = scene.cursor_location
    scene.objects.link(obj)
    scene.objects.active = obj
    mesh.update()


def align_view(obj):
    obj.select = True
    bpy.ops.view3d.view_selected()


def first_edge_ymin(blenderContext):
    """
    Rearranges vertices in a face so the first edge ends at the vertex with minimal Y coordinate
    """
    if not blenderContext.object:
        return
    bpy.ops.object.mode_set(mode="EDIT")
    mesh = blenderContext.object.data
    # setting bmesh instance
    bm = bmesh.from_edit_mesh(blenderContext.object.data)
    if hasattr(bm.faces, "ensure_lookup_table"):
        bm.faces.ensure_lookup_table()
    
    face = bm.faces[0]
    loops = face.loops
    # find the loop with minimal Y coord and minimal X coord
    minY = float("inf")
    maxX = float("-inf")
    loop = loops[0]
    startLoop = loop
    firstLoop = loop
    while True:
        x,y,z = loop.vert.co
        if ( abs(y-minY)<zero and x>maxX ) or y<minY:
            firstLoop = loop
            maxX = x
            minY = y
        loop = loop.link_loop_next
        if loop == startLoop:
            break
    
    firstLoop = firstLoop.link_loop_prev
    
    if firstLoop != startLoop:
        # rearrange vertices
        startLoop = firstLoop
        loop = startLoop
        verts = []
        while True:
            verts.append(loop.vert)
            loop = loop.link_loop_next
            if loop == startLoop:
                break
        bmesh.ops.delete(bm, geom=(face,), context=3)
        bm.faces.new(verts)
        # update mesh
        bmesh.update_edit_mesh(mesh)
    
    bpy.ops.object.mode_set(mode="OBJECT")