import pro
from pro import context

class Extrude2(pro.op_extrude2.Extrude2):
    def execute(self):
        state = context.getState()
        shapesWithRule = state.shape.extrude2(self.parts, self)
        # apply the rule for each shape in shapesWithRule list
        for entry in shapesWithRule:
            context.pushState(shape=entry[0])
            entry[1].execute()
            context.popState()