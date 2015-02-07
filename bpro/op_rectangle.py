import pro
from pro import context
from .util import xAxis, yAxis
from .shape import createRectangle

class Rectangle(pro.op_rectangle.Rectangle):
    def execute(self):
        bm = context.bm
        state = context.getState()
        shape = state.shape
        # get rectangle origin
        origin = shape.center()
        if self.replace:
            shape.delete()
        xVec = self.xSize/2 * xAxis
        yVec = self.ySize/2 * yAxis
        state.shape = createRectangle((
            bm.verts.new(origin - xVec - yVec),
            bm.verts.new(origin + xVec - yVec),
            bm.verts.new(origin + xVec + yVec),
            bm.verts.new(origin - xVec + yVec)
        ))