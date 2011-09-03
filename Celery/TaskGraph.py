import cPickle
import uuid
import networkx
import redis

class TaskGraph(networkx.MultiDiGraph):

    def __init__(self):
        networkx.MultiDiGraph.__init__(self)




class TaskNode(object):

    def __init__(self,func,id=None):
        self.func = func
        self.nodeID = uuid.uuid1() or id

    def __repr__(self):
        funcrep = ".".join([self.func.__module__,self.func.__name__])
        return "TaskNode(%s,id='%s')" % (funcrep,self.idToString())

    def idToString(self):
        return str(self.nodeID)


