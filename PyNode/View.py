from PyQt4 import QtGui
from PyQt4 import QtSvg
from PyQt4 import QtCore

class GraphView(QtGui.QGraphicsView):
    
    def __init__(self, parent=None):
        QtGui.QGraphicsView.__init__(self,parent=parent)
        self.setSceneRect(0,0,10000,100000)
        self.setDragMode(QtGui.QGraphicsView.ScrollHandDrag)
        
    
    """
    def mousePressed(self,event):
        self.last_point = event.pos()
    
 
    def mouseMoveEvent(self,event):
        delta = event.pos() - self.last_point #Get the mouse change
        self.last_point = event.pos() #Update the position of the mouse
        center_on = self.center + delta
        self.centerOn(QtCore.QPointF(center_on.x(),center_on.y())) #Pan, updates the scrollbars to the correct place
    

    def getVisibleCenter(self):
        sceneBounds = self.sceneRect()
    """