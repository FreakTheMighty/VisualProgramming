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
        return "< NodeStage::%s at %s >" % (self.node.name,id(self))

class TaskGraph(networkx.MultiDiGraph):

    def __init__(self):
        networkx.MultiDiGraph.__init__(self)

    def entryPoints(self):
        innodes = []
        for node in self.nodes():
            if not self.in_edges(node):
                innodes.append(self.runNode(node))
        return innodes

    def runNode(self,node):
        return NodeStage(self,node)

class TaskNode(object):

    def __init__(self,id=None):
        """TaskNode is meant to be subclassed.  An instance of that subclass will be run on the farm
        with its input and outputs defined by the isntance's location in the TaskGraph.  The forward definition
        of the nodeID with a UUID allows each Task in the graph to have full picture of the state of the rest of the 
        graph."""
        self.nodeID = uuid.uuid1() or id
        self.name = self.__class__.__name__
        self.pos = (10,10)

    def __repr__(self):
        return "TaskNode(%s,id='%s')" % (self.__class__.__name__,self.idToString())

    def idToString(self):
        """Casts the uuid to a string."""
        return str(self.nodeID)

    def argCount(self):
        """Abstract method responsible for reporting the number available connections."""
        raise NotImplementedError

    def func(self,*args,**kwargs):
        """Abstract method, represents the meat of the Task, executes code and produces results."""
        raise NotImplementedError


class Plug(TaskNode):

    def __init__(self,id=None):
        """A plug is node that doesn't require execution.  This can be used to
        provide client side interaction an entry point into the graph.  For example
        a Qt signal might hook into a plug to provide user options to nodes in the graph."""
        TaskNode.__init__(self,id=id)
        self.juice = None

    def argCount(self):
        return 0

    def func (self):
        return self.juice


class NodeRunner(Task):

    def __init__(self):
        """NodeRunner is a subclass of Celery's Task class.  It is responsible for running tasks
        on the queue and dispatching down stream Tasks."""
        Task.__init__(self)

    def run(self, graph, node, *args,**kwargs):
        """This function is called by celery."""

        #Get incomming products
        positional,keyword = getUpstreamProduct(graph, node)
        positional.extend(args)
        keyword.update(kwargs)
        #execute the node
        result = node.func(*positional,**keyword)
        print result
        setResult(node,result)

        forExecution = downstreamStatus(graph,node)
        for node in forExecution:
            task = NodeRunner()
            task.delay(graph,node)


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
    """Returns a list of values produced by nodes who's outputs are not connected.  IT is useful 
    examining a graph as if it were itself a task."""
    results = []
    for node in graph.nodes():
        if graph.in_edges(node) and not graph.out_edges(node):
            results.append(getNodeProduct(node))
    return results

def setResult(node,value):
    """Sets a value in a node's result location based on the node's UUID."""
    RedisConnect.conn.set(node.idToString(),cPickle.dumps(value))


