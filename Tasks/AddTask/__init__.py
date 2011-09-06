import Flopy.Flow.TaskGraph as TaskGraph

class AddTask(TaskGraph.TaskNode):

    def __init__(self):
        TaskGraph.TaskNode.__init__(self)

    def argCount(self):
        return 2

    def func(self,a,b):
        return a + b

