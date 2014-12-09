import pro
from pro import context

class Join(pro.op_join.Join):
    def execute(self):
        shape = context.getState().shape
        context.addDeferred(shape, self)
    
    def resolve(self, deferred):
        context.joinManager.process(deferred)
