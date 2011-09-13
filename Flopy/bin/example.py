#!/usr/bin/env python

import Flopy.Flow.TaskGraph as TaskGraph
import Tasks.AddTask as AddTask
import time
from yapsy.PluginManager import PluginManager

def run():
    
    # Build the manager
    simplePluginManager = PluginManager()
    # Tell it the default place(s) where to find plugins
    simplePluginManager.setPluginPlaces(["path/to/myplugins"])
    # Load all plugins
    simplePluginManager.collectPlugins()
    
    # Activate all loaded plugins
    print simplePluginManager.getAllPlugins()
    graph = TaskGraph.TaskGraph()

    #So lets see, AddTask is a subclass of TaskNode.
    #TaskNodes contain all the information needed for the actual
    #execution, but are not executed directly.
    a = AddTask.AddTask()
    b = AddTask.AddTask()
    c = AddTask.AddTask()

    graph.add_node(a)
    graph.add_node(b)
    graph.add_node(c)

    graph.add_edge(a,b,0)
    graph.add_edge(c,b,1)
    
    graph.add_edge(a,b,0)
    graph.add_edge(c,b,1)
    
    #entryPoints returns a NodeStage object containing 
    #each node task that has no inputs - this allows a user to interactively.
    #Apply inputs to the nodes.
    #NodeStage objects are a light wrapper for launching a TaskNode onto 
    #the queue
    in1,in2 = graph.entryPoints()
    in1.delay(5,2)
    in2.delay(2,2)

    #The sleep should be replaced with a wait
    time.sleep(.25)
    print TaskGraph.getGraphProducts(graph)
    return graph

if __name__ == "__main__":
    run()
