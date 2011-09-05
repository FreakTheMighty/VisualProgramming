import math

import TaskGraph

def run():
    graph = TaskGraph.TaskGraph()
    a = graph.add_task(math.pow)
    b = graph.add_task(math.pow)
    c = graph.add_task(math.pow)
    
    graph.add_edge(a,b,0)
    graph.add_edge(c,b,1)
    
    in1,in2 = graph.entryPoints()
    in1.delay(5,2)
    in2.delay(2,2)
    return graph
