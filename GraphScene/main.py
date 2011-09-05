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



    sys.exit(app.exec_())
