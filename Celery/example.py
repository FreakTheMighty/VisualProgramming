import math

from tasks import  Node
import TaskGraph

g = TaskGraph.TaskGraph()
a = TaskGraph.TaskNode(math.pow) #Meta Data
b = TaskGraph.TaskNode(math.pow)
c = TaskGraph.TaskNode(math.pow)

g.add_edge(a,b)
g.add_edge(c,b)

t = Node() #Task
t1 = Node()
t.delay(g,a,2,2)
t1.delay(g,c,5,2)
