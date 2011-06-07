from MainView import Ui_MainWindow
from PyQt4 import QtGui
from PyQt4 import QtSvg
from PyQt4 import QtCore

import networkx

import Nodes
import NodeOps

class GraphController(QtGui.QMainWindow, Ui_MainWindow):

    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        self.setupUi(self)
        self.scene = QtGui.QGraphicsScene()
        self.scene.setBackgroundBrush(QtGui.QBrush(QtGui.QPixmap("./resources/grid.jpg")))
        self.graphicsView.setScene(self.scene)
        self.comboBox.addItems(NodeOps.Engine.listOperators())
        self.connect(self.addNodeButton,  QtCore.SIGNAL('clicked(bool)'), self.addNode)
        self.connect(self.runButton,  QtCore.SIGNAL('clicked(bool)'), self.runScript)
        self.connect(self.stepButton,  QtCore.SIGNAL('clicked(bool)'), self.stepThroughScript)

        self.nodes = []
        self.compiled = None
        
    def addNode(self,val):
        nodeName = self.comboBox.currentText()
        node = Nodes.NodeOpGroup(self, nodeName, self.scene)
        self.nodes.append(node)
        
    def stepThroughScript(self):
        if self.compiled:
            try:
                self.compiled.next()
            except StopIteration:
                self.compiled = None
                print "End of script reached"
        else:
            self.compiled = self.constructGraph()
            try:
                self.compiled.next()
            except StopIteration:
                self.compiled = None
                print "End of script reached"
                
    def runScript(self,val):
        [i for i in self.constructGraph()]      
        
    def constructGraph(self):
        sources = []
        graph = networkx.nx.DiGraph()
        for node in self.nodes:
            if node.inputs or node.outputs:
                if not node.inputs:
                    sources.append(node)
                graph.add_node(node)
                
        for node in self.nodes:
            if node.inputs or node.outputs:
                for output in node.outputs:
                    if node != output.node:
                        graph.add_edge(node,output.node)
             
    
        top_sort = networkx.algorithms.dag.topological_sort(graph)
        print top_sort
        for node in top_sort:
            inputs = [input.compiled for input in graph.reverse().neighbors(node)]
            node.compiled = NodeOps.Engine.generatorWrapper(node.func,len(node.outputs),*inputs)
            
        return top_sort[-1].compiled