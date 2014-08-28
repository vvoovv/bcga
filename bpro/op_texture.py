import os
import bpy

from pro import context
from pro.base import Operator


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
            shape.setUV(self.layer, self.width, self.height)
            # now deal with the related material
            materialCache = context.materialCache
            path = self.path
            name = os.path.basename(path)
            # we use the path to the texture as the key of materialCache
            if name in materialCache:
                materialIndex = materialCache[name]
                blenderTexture = bpy.context.object.data.materials[materialIndex].texture_slots[name].texture
            else:
                blenderTexture = bpy.data.textures.new(name, type = "IMAGE")
                blenderTexture.image = bpy.data.images.load(path)
                blenderTexture.use_alpha = True
                
                materialIndex = len(bpy.context.object.data.materials)
                material = bpy.data.materials.new(name)
                textureSlot = material.texture_slots.add()
                textureSlot.texture = blenderTexture
                textureSlot.texture_coords = "UV"
                textureSlot.uv_layer = self.layer
                # remember the material for the future use
                materialCache[name] = materialIndex
                bpy.context.object.data.materials.append(material)
            shape.face.material_index = materialIndex
            shape.addUVlayer(self.layer)
            # set preview texture
            shape.face[bm.faces.layers.tex[self.layer]].image = blenderTexture.image