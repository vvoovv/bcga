from .base import context

def delete():
    """
    Deletes the shape
    """
    return context.factory["Delete"]()