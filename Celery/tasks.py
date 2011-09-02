import cPickle
from celery.task import task
from celery.task.sets import subtask
from celery.task import Task
import uuid
import redis

@task
def add(x, y, callback=None):
    print "WOOOT", add.request.id
    result = x + y
    if callback is not None:
        subtask(callback).delay(result)
    return result


@task()
def test(blah):
    return blah


def plus(x,y):
    return x+y

class Node(Task):
    
    def __init__(self):
        self.redis = redis.Redis(host="localhost", port=6379)

    def run(self, graph, node, *args,**kwargs):
        upstreamNodes = graph.in_edges(node)
        upstreamArgs = self.getResults(upstreamNodes)
        upstreamArgs.extend(args)
        result = node.func(*upstreamArgs)
        self.setResult(node,result)

        forExecution = self.checkDownStream(graph,node)
        for node in forExecution:
            task = Node()
            task.delay(graph,node)

    def checkDownStream(self,graph,node):
        """Current graph and current node.  Returns a list of TaskNodes who's upstream results
        are available."""
        #Get the nodes that the current node feeds into
        nodes = graph.out_edges(node)
        downStreamNodes = [node[1] for node in nodes]
        
        #Loop over those nodes and check to see whether the nodes that those
        #down stream nodes depend on are ready
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

    def after_return(self, *args, **kwargs):

        #Check to see whether the redis results needed for
        #the down stream task are finished, if so, launch the task
        print("Task returned: %r" % (self.request, ))

    
@task(base=Node)
def tsum(numbers):
    return sum(numbers)
