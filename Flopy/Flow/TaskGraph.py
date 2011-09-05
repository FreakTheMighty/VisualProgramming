import cPickle
import uuid
import networkx
import redis

from celery.task import Task

class RedisConnect(object):

    conn = redis.Redis(host="localhost", port=6379)

class NodeStage(object):

    def __init__(self,graph,node):
        self.graph = graph
        self.node = node
        self.runner = NodeRunner()

    def delay(self,*args,**kwargs):
        things = [self.graph, self.node] + list(args)
        return self.runner.apply_async(things)

    def __repr__(self):
        funcname = ".".join([self.node.func.__module__,self.node.func.__name__])
        return "< NodeStage::%s at %s >" % (funcname,id(self))

class NodeRunner(Task):

    def __init__(self):
        Task.__init__(self)

    def run(self, graph, node, *args,**kwargs):
        """This function is called by celery."""

        #Get incomming products
        positional,keyword = getUpstreamProduct(graph, node)
        positional.extend(args)
        keyword.update(kwargs)

        #execute the node
        result = node.func(*positional,**keyword)
        setResult(node,result)

        forExecution = downstreamStatus(graph,node)
        for node in forExecution:
            task = NodeRunner()
            task.delay(graph,node)

class TaskGraph(networkx.MultiDiGraph):

    def __init__(self):
        networkx.MultiDiGraph.__init__(self)

    def add_task(self,func):
        task = TaskNode(func)
        self.add_node(task)
        return task

    def entryPoints(self):
        innodes = []
        for node in self.nodes():
            if not self.in_edges(node):
                innodes.append(self.runNode(node))
        return innodes

    def runNode(self,node):
        return NodeStage(self,node)

class TaskNode(object):

    def __init__(self,func,id=None):
        self.func = func
        self.nodeID = uuid.uuid1() or id
        funcrep = ".".join([self.func.__module__,self.func.__name__])
        self.name = "%s:%s" % (funcrep,self.idToString())
        self.pos = (10,10)

    def __repr__(self):
        funcrep = ".".join([self.func.__module__,self.func.__name__])
        return "TaskNode(%s,id='%s')" % (funcrep,self.idToString())

    def idToString(self):
        return str(self.nodeID)

    def argCount(self):
        return 2

def getNodeProduct(node):
    """Get result produced by node, deserialize and return."""
    datastore = RedisConnect.conn.get(node.idToString())
    if datastore is not None:
        return cPickle.loads(datastore)
    else:
        return None

def getOrderedInputs(graph, node):
    """Sort incomming nodes into ordered args and kwargs, based on edge signature"""
    upstreamEdges = graph.in_edges(node)
    pargs= []
    kargs = {}
    for e in upstreamEdges:
        keys = graph.edge[e[0]][e[1]].keys()
        for key in keys:
            if isinstance(key,int):
                pargs.insert(key,e[0])
            else:
                kargs[key] = e[0]
    return pargs,kargs


def getUpstreamProduct(graph,node):
    """Like 'getOrderedInputs', but replaces the list and dictionary of nodes
    with the results that those nodes produced"""
    positional,keyword = getOrderedInputs(graph,node)
    positional = [getNodeProduct(node) for node in positional]
    for key in keyword:
        keyword[key] = getNodeProduct(keyword[key])
    return positional,keyword

def downstreamStatus(graph,node):
    """Current graph and current node.  Returns a list of TaskNodes who's upstream results
    are available."""
    #Get the nodes that the current node feeds into
    nodes = graph.out_edges(node)
    downStreamNodes = [node[1] for node in nodes]
    
    #Loop over the downstream nodes and check to see whether the nodes that those
    #down stream nodes depend on have produced results
    readyToExecute = []
    for node in downStreamNodes:
        pos,kwargs = getUpstreamProduct(graph,node)
        argcount = len(pos) + len(kwargs)
        if len(nodes[0]) == argcount:
            readyToExecute.append(node)
    return readyToExecute

def getGraphProducts(graph):
    results = []
    for node in graph.nodes():
        if graph.in_edges(node) and not graph.out_edges(node):
            results.append(getNodeProduct(node))
    return results

def setResult(node,value):
    RedisConnect.conn.set(node.idToString(),cPickle.dumps(value))

def add(x,y):
    return x + y

def asum(*args):
    return sum(args)

def stubfunc(graph,node,*args,**kwargs):
    runner = NodeRunner()
    runner.delay(graph,node,*args,**kwargs)
