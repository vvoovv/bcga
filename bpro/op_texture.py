import os
import bpy

from pro import context
from pro.base import Operator

from .material import setPreviewTexture


class Texture(Operator):
    
    defaultLayer = "prokitektura"
    
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
            materialRegistry = context.materialRegistry
            path = self.path
            name = os.path.basename(path)
            material = materialRegistry.getMaterial(name)
            if material:
                materialIndex = materialRegistry.getMaterialIndex(name)
            else:
                blenderTexture = bpy.data.textures.new(name, type = "IMAGE")
                blenderTexture.image = bpy.data.images.load(path)
                blenderTexture.use_alpha = True
                
                material = bpy.data.materials.new(name)
                textureSlot = material.texture_slots.add()
                textureSlot.texture = blenderTexture
                textureSlot.texture_coords = "UV"
                textureSlot.uv_layer = self.layer
                materialRegistry.setMaterial(name, material)
                materialIndex = materialRegistry.getMaterialIndex(name)
                
            shape.face.material_index = materialIndex
            shape.addUVlayer(self.layer, self)
            # set preview texture
            setPreviewTexture(shape, materialIndex)