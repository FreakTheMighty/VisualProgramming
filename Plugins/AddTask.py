from Flopy.Flow.TaskGraph import TaskNode

class AddTask(TaskNode):

    NODE_TYPE = "Add"

    def __init__(self):
        TaskNode.__init__(self)

    def argCount(self):
        return 2

    def func(self,a,b):
        return a + b

