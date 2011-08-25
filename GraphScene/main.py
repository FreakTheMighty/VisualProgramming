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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main =  QtGui.QMainWindow()
    main.resize(400,400)

    graph = Nodes.CodeGraph()
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
    projectMng = Nodes.ProjectManager("./TestProject")
    dataMng = Nodes.DataManager(projectMng)
    #Operators
    import Maths
    operator0 = Maths.sumprint()
    operator1 = Maths.add()
    operator2 = Maths.add()
    dataMng.register(operator0,operator1,operator2)

    opsmodel.operators = [operator0,operator1,operator2]
    oploader.setModel(opsmodel)

    graph.add_edge(operator1,operator0,key=0)
    graph.add_edge(operator2,operator0,key=1)
    #graph = yaml.load(open("/tmp/test.yaml"))
    graphscene.addGraph(graph)

    a = Nodes.Packet(0,1)
    b = Nodes.Packet(1,1)
    operator1.send(a)
    operator1.send(b)
    operator2.send(a)
    operator2.send(b)


    sys.exit(app.exec_())
