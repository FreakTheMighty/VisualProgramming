import Flopy.Flow.Operator as Operator

class Add(Operator.TaskNode):

    INTERFACE=[0,1]

    def __init__(self,*args,**kwargs):
        Operator.TaskNode.__init__(self,*args,**kwargs)

    def run(self,a,b):
        return a + b
