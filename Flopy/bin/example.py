#!/usr/bin/env python

import Flopy.Flow.TaskGraph as TaskGraph
import Tasks.AddTask.Operator as Operator
import time

def run():
    graph = TaskGraph.TaskGraph()

    a = Operator.AddTask()
    b = Operator.AddTask()
    c = Operator.AddTask()

    graph.add_node(a)
    graph.add_node(b)
    graph.add_node(c)

    graph.add_edge(a,b,0)
    graph.add_edge(c,b,1)
    
    graph.add_edge(a,b,0)
    graph.add_edge(c,b,1)
    
    in1,in2 = graph.entryPoints()
    in1.delay(5,2)
    in2.delay(2,2)
    #The sleep should be replaced with a wait
    time.sleep(.25)
    print TaskGraph.getGraphProducts(graph)
    return graph

if __name__ == "__main__":
    run()
