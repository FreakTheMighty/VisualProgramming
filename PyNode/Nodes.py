import math
import copy

import PyQt4.QtGui as QtGui
import PyQt4.QtCore as QtCore 
import PyQt4.QtSvg as QtSvg 

from PyQt4.Qt import Qt
from PyQt4.Qt import QEvent

ARROW_OFFSET = (43,47)
BUSH = QtGui.QColor(122,163,39)
PEN = QtGui.QPen(QtGui.QColor(79,80,40),4,
            Qt.SolidLine,Qt.FlatCap,Qt.MiterJoin)

class NodeOpGroup(QtGui.QGraphicsItemGroup):

    def __init__(self,scene=None, parent=None):
        QtGui.QGraphicsItemGroup.__init__(self,scene=scene, parent=parent)
        self.incomming = []
        self.outgoing = []
        
        self.scene = scene
        self.output = Output(self.scene)
        self.input = Input(self.scene)
        self.inPorts = [self.input]
        
        self.path = None
        
        self.operator = NodeOp(self.output, self.scene)
        self.addToGroup(self.operator)
        self.addToGroup(self.output)
        self.addToGroup(self.input)
        self.output.setPos(45,40)
        self.input.setPos(45,-5)

    	self.setFlag(QtGui.QGraphicsItem.ItemIsMovable, True);
    	self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable, True);
    	self.setHandlesChildEvents(False)
        
    def connect(self,node,idx):
        self.outgoing.append(node)
        node.incomming.insert(idx,self)
        
    def disconnect(self,node):
        self.outgoing.remove(node)
        node.incomming.remove(node)
        
class NodeOp(QtSvg.QGraphicsSvgItem):

    def __init__(self,output, scene=None):
    	QtSvg.QGraphicsSvgItem.__init__(self,
					"./resources/NodeOp.svg")
        self.setElementId("NodeOp")
        self.scene = scene
    	self.setFlag(QtGui.QGraphicsItem.ItemIsMovable, True);
    	self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable, True);


    def mouseMoveEvent(self,event):
    	QtSvg.QGraphicsSvgItem.mouseMoveEvent(self,event)
        if self.group().path:
    
            scenePos = self.group().output.scenePos()
            x1 = scenePos.x()+(self.group().output.boundingRect().width()/2)
            y1 = scenePos.y()+(self.group().output.boundingRect().height()/2)
            #scnPos = self.scene.views()[0].mapToScene(x1,y1)
            #x1 = scnPos.x()
            #y1 = scnPos.y()
            
            x2 = self.group().path.line().x2()
            y2 = self.group().path.line().y2()
        	
            line = QtCore.QLineF(x1,y1,x2,y2)
            self.group().path.setLine(line)
        
        if self.group().incomming:
            for idx, node in enumerate(self.group().inPorts):
                x1 = self.group().incomming[idx].path.line().x1()
                y1 = self.group().incomming[idx].path.line().y1()

                scenePos = node.scenePos()
                x2 = scenePos.x()+(node.group().output.boundingRect().width()/2)
                y2 = scenePos.y()+(node.group().output.boundingRect().height()/2)
                

class Output(QtSvg.QGraphicsSvgItem):

    def __init__(self,scene=None,parent=None):
    	QtSvg.QGraphicsSvgItem.__init__(self,
					"./resources/NodeOp.svg")
	
        self.setElementId("output")
        self.scene = scene
        self.parent = parent 
        self.setParentItem(parent)
        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable, True);
        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable, True);

        if scene:
    	   scene.addItem(self)


    def mouseMoveEvent(self,event):
        
        if not self.group().path:
            self.group().path = self.scene.addLine(QtCore.QLineF(0,0,0,0),PEN)
            self.group().path.setZValue(-1000)

        scenePos = self.scenePos()
        x1 = scenePos.x()+(self.boundingRect().width()/2)
        y1 = scenePos.y()+(self.boundingRect().height()/2)
        x2 = event.scenePos().x()
        y2 = event.scenePos().y()
	
        line = QtCore.QLineF(x1,y1,x2,y2)
        self.group().path.setLine(line)
        
    def mouseReleaseEvent(self,event):  
        if self.group().path:
            view = self.scene.views()[0]
            underWidgets = self.scene.items(self.group().path.line().p2())
            widget = [w for w in underWidgets if isinstance(w,Input)]
            if not widget:
                self.scene.removeItem(self.group().path)
                self.group().path = None
            else:
                self.group().connect(widget[0].group(),0)
                
class Input(QtSvg.QGraphicsSvgItem):

    def __init__(self,scene=None,parent=None):
        QtSvg.QGraphicsSvgItem.__init__(self,
                    "./resources/NodeOp.svg")
    
        self.setElementId("input")
        self.scene = scene
        self.parent = parent 
        self.setParentItem(parent)
        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable, True);
        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable, True);
        self.setAcceptDrops(True)
        if scene:
           scene.addItem(self)
        
        brush = QtGui.QColor(122,163,39)
        pen = QtGui.QPen(QtGui.QColor(79,80,40),4,
                    Qt.SolidLine,Qt.FlatCap,Qt.MiterJoin)
    
    def mouseMoveEvent(self,event):
        pass
    
    def dragEnterEvent(self,event):
        print "DROPPED"
