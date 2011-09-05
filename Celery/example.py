import math

from tasks import  NodeRunner
import TaskGraph

def run():
    graph = TaskGraph.TaskGraph()
    #a = TaskGraph.TaskNode(math.pow)
    #b = TaskGraph.TaskNode(math.pow)
    #c = TaskGraph.TaskNode(math.pow)
    #
    graph.add_edge(math.pow,math.pow,0)
    graph.add_edge(math.pow,math.pow,1)
    
    t = TaskGraph.NodeRunner() #Task
    t1 = TaskGraph.NodeRunner()
    t1.delay(graph,c,5,2)
    t.delay(graph,a,2,2)
    return graph
