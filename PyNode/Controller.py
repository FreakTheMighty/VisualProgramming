
from MainView import Ui_MainWindow
from PyQt4 import QtGui
from PyQt4 import QtSvg
import Nodes

class GraphController(QtGui.QMainWindow, Ui_MainWindow):

    def __init__(self, parent=None):
	QtGui.QMainWindow.__init__(self, parent)
	self.setupUi(self)
	self.scene = QtGui.QGraphicsScene()
	self.scene.setBackgroundBrush(
		QtGui.QBrush(QtGui.QPixmap("./resources/grid.jpg")))
        self.graphicsView.setScene(self.scene)
        nodeGroup =  Nodes.NodeOpGroup(self.scene)


