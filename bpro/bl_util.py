import bpy
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
    obj.select = True
    bpy.ops.view3d.view_selected()
    mesh.update()