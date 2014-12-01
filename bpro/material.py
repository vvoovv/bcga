import bpy

from pro import context


class MaterialRegistry:
    
    def __init__(self):
        # a dict materialName->materialIndex, where materialIndex is the material index for the active Blender object
        self.reg = {}
    
    def getMaterial(self, name):
        """
        Returns Blender material for the specified name or None if the material doesn't exist
        for the given name
        """
        material = None 
        reg = self.reg
        objectMaterials = bpy.context.object.data.materials
        allMaterials = bpy.data.materials
        if name in self.reg:
            # we have already met that material before
            materialIndex = self.reg[name]
            material = objectMaterials[materialIndex]
        elif name in objectMaterials:
            # The material was set for the active Blender object before
            # the current rule set had been applied to it
            material = objectMaterials[name]
            # find materialIndex
            for materialIndex in range(len(objectMaterials)):
                if objectMaterials[materialIndex] == material:
                    break
            self.reg[name] = materialIndex
        elif name in allMaterials:
            # The material is already available, but not yet used by the active Blender object
            material = allMaterials[name]
            self.setMaterial(name, material)
        return material
    
    def setMaterial(self, name, material):
        """
        Appends the material to the active Blender object and register it with self.reg
        """
        objectMaterials = bpy.context.object.data.materials
        materialIndex = len(objectMaterials)
        objectMaterials.append(material)
        self.reg[name] = materialIndex
    
    def getMaterialIndex(self, name):
        return self.reg[name]
    
    def createMaterial(self, name, textures):
        """
        Creates a new material and calls self.setMaterial(...)
        """
        engine = context.blenderContext.scene.render.engine
        if engine=="BLENDER_RENDER":
            material = createBlenderRenderMaterial(name, textures)
        elif engine=="CYCLES":
            material = createCyclesRenderMaterial(name, textures)
        self.setMaterial(name, material)


def setPreviewTexture(shape, materialIndex):
    # a slot for the texture
    materials = bpy.context.object.data.materials
    if len(materials)==0: return
    slot = materials[materialIndex].texture_slots[0]
    if slot:
        shape.face[context.bm.faces.layers.tex.active].image = slot.texture.image


def createBlenderRenderMaterial(name, textures):
    texture = textures[0]
    # create Blender texture
    blenderTexture = bpy.data.textures.new(name, type = "IMAGE")
    blenderTexture.image = bpy.data.images.load(texture.path)
    blenderTexture.use_alpha = True

    material = bpy.data.materials.new(name)
    textureSlot = material.texture_slots.add()
    textureSlot.texture = blenderTexture
    textureSlot.texture_coords = "UV"
    textureSlot.uv_layer = texture.layer
    
    return material


def createCyclesRenderMaterial(name, textures):
    pass