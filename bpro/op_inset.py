import pro
from pro import context
from .polygon import Polygon
from .polygon_manager import Manager
from .op_delete import Delete

class Inset(pro.op_inset.Inset):
    def execute(self):
        shape = context.getState().shape
        face = shape.face
        manager = Manager()
        polygon = Polygon(face.verts, face.normal, manager)
        manager.rule = self.side
        kwargs = {"height": self.height} if self.height else {}
        polygon.inset(*self.insets, **kwargs)
        # create a shape for the cap if necessary
        cap = self.cap
        if not isinstance(cap, Delete):
            shape = polygon.getShape(type(shape))
            if cap:
                context.pushState(shape=shape)
                self.cap.execute()
                context.popState()
        #shape.delete()
        # finalizing: if there is a rule for the shape, execute it
        for entry in manager.shapes:
            context.pushState(shape=entry[0])
            entry[1].execute()
            context.popState()