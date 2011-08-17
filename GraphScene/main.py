#!/usr/bin/env python

#Standard libraries
import sys

#Third party libraries
from PyQt4.QtGui import QApplication
from PyQt4 import QtCore, QtGui
import networkx
import yaml

#Core libraries
import Graph
import Nodes

#Operators
import TestProject.Operators as Operators

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main =  QtGui.QMainWindow()
    main.resize(400,400)

    graph = networkx.MultiDiGraph()
    view = QtGui.QGraphicsView()
    graphscene= Graph.GraphScene(graph)

    oploader = Graph.OpLoader(graphscene)
    graphscene.oploader = oploader
    oploader.setGeometry(0,0,200,30)
    opsmodel = Graph.OperatorsModel()
    completer = QtGui.QCompleter(opsmodel)
    completer.setCompletionMode(1)


    graphscene.setParent(view)
    view.setScene(graphscene)

    main.setCentralWidget(view)
    main.show()

    #Node Objects
    operator0 = Nodes.Node(Operators.add)
    operator1 = Nodes.Node(Operators.add)
    operator2 = Nodes.Node(Operators.add)

    opsmodel.operators = [operator0,operator1,operator2]
    oploader.setModel(opsmodel)

    graph.add_edge(operator1,operator0,key=0)
    graph.add_edge(operator2,operator0,key=1)
    #graph = yaml.load(open("/tmp/test.yaml"))
    graphscene.addGraph(graph)



    sys.exit(app.exec_())
