from .base import context

def texture(path="", width=0, height=0, **kwargs):
    """
    Sets a texture for the 2D-shape
    
    Args:
      path: path to the texture
      width: texture width in the units of global coordinate system
      height: texture height in the units of global coordinate sytem
    """
    return context.factory["Texture"](path, width, height, **kwargs)