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
        self.connect(self.addNodeButton,  QtCore.SIGNAL('clicked(bool)'), self.onAddNode)
        self.connect(self.runButton,  QtCore.SIGNAL('clicked(bool)'), self.runScript)
        self.connect(self.stepButton,  QtCore.SIGNAL('clicked(bool)'), self.stepThroughScript)


        self.nodes = []
        self.compiled = None

    def on_actionSave_As_triggered(self,checked=None):
        if checked == False:
            graph = self.constructSceneGraph()
            filepath = QtGui.QFileDialog.getSaveFileName(self, "FileDialog")
            if filepath:
                networkx.readwrite.graphml.write_graphml(graph,str(filepath))
        
    def on_actionOpen_triggered(self,checked=None):
        if checked == None:
            filepath = QtGui.QFileDialog.getOpenFileName (self, "FileDialog")
            print filepath
            if filepath:
                graph = networkx.readwrite.graphml.read_graphml(str(filepath))
                self.loadGraph(graph)
                
    def loadGraph(self,graph):
        for node in graph.node:
            new_node = self.addNode(graph.node[node]["func_name"])
            graph.node[node]["Object"] = new_node
            new_node.setTitle(str(node))
            posx = graph.node[node]["posx"]
            posy = graph.node[node]["posy"]
            new_node.setPos(posx,posy)
            
        graph = graph.reverse()
        for node in graph:
            for idx, neighbor in enumerate(graph.neighbors(node)):
                #print idx,neighbor
                graph.node[node]["Object"].connectInput(graph.node[neighbor]["Object"],idx)
                
    def onAddNode(self,val):
        nodeName = self.comboBox.currentText()
        self.addNode(nodeName)
        
    def addNode(self,nodeName):
        node = Nodes.NodeOpGroup(self, nodeName, self.scene)
        self.nodes.append(node)
        return node

    def stepThroughScript(self):
        print self.compiled
        if not self.compiled:
            self.compiled = self.compileGraph()

        for output in self.compiled:
            try:
                print output.next()
            except StopIteration:
                self.compiled = None
                print "End of script reached"

    def runScript(self,val):
        if not self.compiled:
            self.compiled =self.compileGraph()

        for output in self.compiled:
            for step in output:
                step

    def constructSceneGraph(self):
        sources = []
        graph = networkx.nx.DiGraph()
        for node in self.nodes:
            if node.inputs or node.outputs:
                if not node.inputs:
                    sources.append(node)
                graph.add_node(str(node.title.toPlainText()),
                               func_name = node.func.func_name,
                               posx = node.pos().x(),
                               posy = node.pos().y())
                
        for node in self.nodes:
            if node.inputs or node.outputs:
                for output in node.outputs:
                    if node != output.node:
                        graph.add_edge(str(node.title.toPlainText()),
                                       str(output.node.title.toPlainText()))
        return graph
            
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
        return graph
    
    def compileGraph(self):
        graph = self.constructGraph()
        top_sort = networkx.algorithms.dag.topological_sort(graph)
        for node in top_sort:
            inputs = [input.compiled for input in graph.reverse().neighbors(node)]
            node.compiled = NodeOps.Engine.generatorWrapper(node.func,len(node.outputs),node.widget,*inputs)
            
        outputs = []
        reversed = graph.reverse()
        
        for node in top_sort:
            if len( graph.neighbors(node) ) == 0:
                outputs.append(node.compiled)
        
        return outputs
    
class CodeThread(QtCore.QObject):
    
    def __init__(self,graph, parent=None):
        QtCore.QObject.__init__(parent=parent)
        self.graph = graph
        
    
    