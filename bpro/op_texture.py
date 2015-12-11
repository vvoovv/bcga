import os
import bpy

from pro import context
from pro.base import Operator


class Texture(Operator):
    
    defaultLayer = "bcga"
    
    def __init__(self, path, width, height, **kwargs):
        self.path = os.path.join(os.path.dirname(context.ruleFile), "assets", path)
        self.layer = kwargs["layer"] if "layer" in kwargs else self.defaultLayer
        self.width = width
        self.height = height
        super().__init__()
    
    def execute(self):
        shape = context.getState().shape
        bm = context.bm
        if self.path=="" and self.width==0 and self.height==0:
            pass
        else:
            shape.setUV(self.layer, self)
            # now deal with the related material
            materialManager = context.materialManager
            path = self.path
            name = os.path.basename(path)
            material = materialManager.getMaterial(name)
            if not material:
                material = materialManager.createMaterial(name, (self,))
            if material:
                materialIndex = materialManager.getMaterialIndex(name)
                shape.face.material_index = materialIndex
                # set preview texture
                materialManager.setPreviewTexture(shape, materialIndex)