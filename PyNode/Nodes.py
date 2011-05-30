import math
import copy

import PyQt4.QtGui as QtGui
import PyQt4.QtCore as QtCore 
import PyQt4.QtSvg as QtSvg 

from PyQt4.Qt import Qt
from PyQt4.Qt import QEvent

ARROW_OFFSET = (43,47)

class NodeOpGroup(QtGui.QGraphicsItemGroup):

    def __init__(self,scene=None, parent=None):
        QtGui.QGraphicsItemGroup.__init__(self,scene=scene, parent=parent)
        self.scene = scene
        self.output = Output(self.scene)
	self.operator = NodeOp(self.output, self.scene)
	self.addToGroup(self.operator)
	self.addToGroup(self.output)
	self.output.setPos(50,40)
    	self.setFlag(QtGui.QGraphicsItem.ItemIsMovable, True);
    	self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable, True);
    	self.setHandlesChildEvents(False)


class NodeOp(QtSvg.QGraphicsSvgItem):

    def __init__(self,output, scene=None):
    	QtSvg.QGraphicsSvgItem.__init__(self,
					"./resources/NodeOp.svg")
	self.setElementId("NodeOp")
	self.scene = scene
	self.output = output
    	self.setFlag(QtGui.QGraphicsItem.ItemIsMovable, True);
    	self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable, True);


    def mouseMoveEvent(self,event):
	QtSvg.QGraphicsSvgItem.mouseMoveEvent(self,event)
	scenePos = self.output.scenePos()
	x1 = scenePos.x()+(self.output.boundingRect().width()/2)
	y1 = scenePos.y()+(self.output.boundingRect().height()/2)
	x2 = self.output.path.line().x2()
	y2 = self.output.path.line().y2()
	
	line = QtCore.QLineF(x1,y1,x2,y2)
	self.output.path.setLine(line)

class Output(QtSvg.QGraphicsSvgItem):

    def __init__(self,scene=None,parent=None):
    	QtSvg.QGraphicsSvgItem.__init__(self,
					"/home/jvanderdoes/Documents/dev/PyNode/resources/NodeOp.svg")
	
	self.setElementId("arrow")
	self.scene = scene
	self.parent = parent 
	self.setParentItem(parent)
    	self.setFlag(QtGui.QGraphicsItem.ItemIsMovable, True);
    	self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable, True);

	if scene:
	    scene.addItem(self)
    
	brush = QtGui.QColor(122,163,39)
	pen = QtGui.QPen(QtGui.QColor(79,80,40),4,
			    Qt.SolidLine,Qt.FlatCap,Qt.MiterJoin)

	self.path = self.scene.addLine(QtCore.QLineF(0,0,0,0),pen)
	self.path.setZValue(-1000)

    def mouseMoveEvent(self,event):
	scenePos = self.scenePos()
	x1 = scenePos.x()+(self.boundingRect().width()/2)
	y1 = scenePos.y()+(self.boundingRect().height()/2)
	x2 = event.scenePos().x()
	y2 = event.scenePos().y()
	
	line = QtCore.QLineF(x1,y1,x2,y2)
	self.path.setLine(line)

