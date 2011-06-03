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
        if self.group().output.paths:
    
            for idx, path in enumerate(self.group().output.paths):
                scenePos = self.group().output.scenePos()
                x1 = scenePos.x()+(self.group().output.boundingRect().width()/2)
                y1 = scenePos.y()+(self.group().output.boundingRect().height()/2)
            
                x2 = self.group().output.paths[idx].line().x2()
                y2 = self.group().output.paths[idx].line().y2()
            	
                line = QtCore.QLineF(x1,y1,x2,y2)
                path.setLine(line)
                
        if self.group().input.nodes:
            
            for idx, node in enumerate(self.group().input.nodes):
                x1 = node.output.paths[idx].line().x1()
                y1 = node.output.paths[idx].line().y1()
                
                scenePos = self.group().input.scenePos()
                x2 = scenePos.x()+(self.group().input.boundingRect().width()/2)
                y2 = scenePos.y()+(self.group().input.boundingRect().height()/2)
                line = QtCore.QLineF(x1,y1,x2,y2)
                index = node.output.nodes.index(self.group())
                node.output.paths[index].setLine(line)


class Output(QtSvg.QGraphicsSvgItem):

    def __init__(self,scene=None,parent=None):
    	QtSvg.QGraphicsSvgItem.__init__(self,
					"./resources/NodeOp.svg")
	
        self.paths = []
        self.nodes = []
        self.setElementId("output")
        self.scene = scene
        self.parent = parent 
        self.setParentItem(parent)
        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable, True);
        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable, True);

        self.dragPhase = 1
        
        if scene:
    	   scene.addItem(self)


    def mouseMoveEvent(self,event):
        if self.scene.itemAt(event.scenePos()) == self and self.dragPhase:
            self.dragPhase = 0
            path = self.scene.addLine(QtCore.QLineF(0,0,0,0),PEN)
            path.setZValue(-1000)
            self.paths.append(path)
            
        scenePos = self.scenePos()
        x1 = scenePos.x()+(self.boundingRect().width()/2)
        y1 = scenePos.y()+(self.boundingRect().height()/2)
        x2 = event.scenePos().x()
        y2 = event.scenePos().y()
	
        line = QtCore.QLineF(x1,y1,x2,y2)
        self.paths[-1].setLine(line)
        
    def mouseReleaseEvent(self,event):  
        if self.paths:
            view = self.scene.views()[0]
            underWidgets = self.scene.items(self.paths[-1].line().p2())
            widget = [w for w in underWidgets if isinstance(w,Input)]
            if not widget:
                self.scene.removeItem(self.paths[-1])
                self.paths.pop(-1)
                for node in self.nodes:
                    if self in node.input.nodes:
                        node.input.nodes.remove(self)
            else:
                if len(widget[0].group().input.nodes) < 1:
                    widget[0].group().input.nodes.append(self.group())
                    self.nodes.append(widget[0].group())
                else:
                    self.scene.removeItem(self.paths[-1])
                    self.paths.pop(-1)

        self.dragPhase = 1
        
class Input(QtSvg.QGraphicsSvgItem):

    def __init__(self,scene=None,parent=None):
        QtSvg.QGraphicsSvgItem.__init__(self,
                    "./resources/NodeOp.svg")
    
        self.nodes = []
        
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
        for node in self.nodes:
            scenePos = node.output.scenePos()
            x1 = scenePos.x()+(self.boundingRect().width()/2)
            y1 = scenePos.y()+(self.boundingRect().height()/2)
            x2 = event.scenePos().x()
            y2 = event.scenePos().y()
    
            line = QtCore.QLineF(x1,y1,x2,y2)
            node.output.paths[-1].setLine(line)
    
    def mouseReleaseEvent(self,event):  
        view = self.scene.views()[0]
        for node in self.nodes:
            index = node.output.nodes.index(self.group())
            underWidgets = self.scene.items(node.output.paths[index].line().p2())
            if self in underWidgets:
                x1 = node.output.paths[index].line().x1()
                y1 = node.output.paths[index].line().y1()
                
                scenePos = self.scenePos()
                x2 = scenePos.x()+(self.boundingRect().width()/2)
                y2 = scenePos.y()+(self.boundingRect().height()/2)
                line = QtCore.QLineF(x1,y1,x2,y2)
                node.output.paths[index].setLine(line)
            else:
                self.scene.removeItem(node.output.paths[index])
                self.nodes.remove(node)
                node.output.nodes.remove(self.group())

       