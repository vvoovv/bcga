import bpy
import pro
from pro import context


class Material(pro.op_material.Material):
    def execute(self):
        materialManager = context.materialManager
        material = materialManager.getMaterial(self.material)
        if material:
            materialIndex = materialManager.getMaterialIndex(self.material)

            # assign material to the bmesh face
            shape = context.getState().shape
            shape.clearUVlayers()
            shape.face.material_index = materialIndex
