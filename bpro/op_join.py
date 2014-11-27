import pro
from pro import context

class Join(pro.op_join.Join):
    def execute(self):
        shape = context.getState().shape
        context.addDeferred(shape, self)
    
    def resolve(self, shape):
        neighbor = self.neighbor
        if neighbor=="right":
            neighbor = shape.firstLoop.link_loop_next.link_loops[0].face
        elif neighbor=="left":
            neighbor = shape.firstLoop.link_loop_prev.link_loops[0].face
