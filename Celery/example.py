import math

from tasks import  NodeRunner
import TaskGraph

graph = TaskGraph.TaskGraph()
a = TaskGraph.TaskNode(math.pow)
b = TaskGraph.TaskNode(math.pow)
c = TaskGraph.TaskNode(math.pow)

graph.add_edge(a,b)
graph.add_edge(c,b)

t = NodeRunner() #Task
t1 = NodeRunner()
t.delay(graph,a,2,2)
t1.delay(graph,c,5,2)
