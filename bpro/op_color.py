import bpy
import pro
from pro import context


class Color(pro.op_color.Color):
    def execute(self):
        materialManager = context.materialManager
        colorHex = self.colorHex
        material = materialManager.getMaterial(colorHex)
        if material:
            materialIndex = materialManager.getMaterialIndex(colorHex)
        else:
            material = bpy.data.materials.new(colorHex)
            material.diffuse_color = self.color + (0xff,)
            materialManager.setMaterial(colorHex, material)
            materialIndex = materialManager.getMaterialIndex(colorHex)
        # assign material to the bmesh face
        shape = context.getState().shape
        shape.clearUVlayers()
        shape.face.material_index = materialIndex
