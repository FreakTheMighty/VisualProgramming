#!/usr/bin/env python
import sys
from PyQt4.QtGui import QApplication
from PyQt4 import QtCore, QtGui
import Graph
import Nodes
import networkx
import yaml

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
    operator0 = Nodes.Node("operator0")
    operator0.in_count  = 4
    operator1 = Nodes.Node("operator1")
    operator2 = Nodes.Node("operator2")

    opsmodel.operators = [operator0,operator1,operator2]
    oploader.setModel(opsmodel)

    graph.add_edge(operator1,operator0,key=0)
    graph.add_edge(operator2,operator0,key=1)
    #graph = yaml.load(open("/tmp/test.yaml"))
    graphscene.addGraph(graph)



    sys.exit(app.exec_())
