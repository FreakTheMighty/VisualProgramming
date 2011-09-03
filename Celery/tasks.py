import cPickle
from celery.task import task
from celery.task.sets import subtask
from celery.task import Task
import uuid
import redis


class NodeRunner(Task):
    
    Task.name = "WOOT"

    def __init__(self,name=None):
        self.redis = redis.Redis(host="localhost", port=6379)

    def run(self, graph, node, *args,**kwargs):
        """This function is called by celery."""
        upstreamNodes = graph.in_edges(node)
        upstreamArgs = self.getResults(upstreamNodes)
        upstreamArgs.extend(args)
        result = node.func(*upstreamArgs)
        self.setResult(node,result)

        forExecution = self.checkDownStream(graph,node)
        for node in forExecution:
            task = NodeRunner()
            task.delay(graph,node)

    def sortUpstreamResults(self,graph,node):
        """This function will be responsible for taking the edge keywords and
        organizing the arguments.  Positional arguments will be sorted and keyword arguments
        seperated"""
        raise NotImplementedError

    def checkDownStream(self,graph,node):
        """Current graph and current node.  Returns a list of TaskNodes who's upstream results
        are available."""
        #Get the nodes that the current node feeds into
        nodes = graph.out_edges(node)
        downStreamNodes = [node[1] for node in nodes]
        
        #Loop over the downstream nodes and check to see whether the nodes that those
        #down stream nodes depend on have produced results
        readyToExecute = []
        for node in downStreamNodes:
            nodes = graph.in_edges(node)
            if not None in self.getResults(nodes):
                readyToExecute.append(node)
        return readyToExecute

    def setResult(self, node,value):
        self.redis.set(node.idToString(),cPickle.dumps(value))

    def getResults(self,nodes):
        results = []
        for node in nodes:
            datastore = self.redis.get(node[0].idToString())
            if datastore:
                result = cPickle.loads(datastore)
            else:
                result = None
            results.append(result)
        return results

