from .base import context

def texture(path="", width=0, height=0, **kwargs):
    """
    Sets a texture for the 2D-shape
    
    Args:
        path: Path to the texture
        width: Texture width in the units of global coordinate system
        height: Texture height in the units of global coordinate sytem
    """
    # treat the special case when path is actually a tuple (path, width, height)
    if isinstance(path, (tuple, list)):
        path, width, height = path
    return context.factory["Texture"](path, width, height, **kwargs)