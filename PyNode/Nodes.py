import math
import copy

import PyQt4.QtGui as QtGui
import PyQt4.QtCore as QtCore 
import PyQt4.QtSvg as QtSvg 

from PyQt4.Qt import Qt
from PyQt4.Qt import QEvent

import NodeOps

ARROW_OFFSET = (43,47)
BUSH = QtGui.QColor(122,163,39)
PEN = QtGui.QPen(QtGui.QColor(79,80,40),4,
            Qt.SolidLine,Qt.FlatCap,Qt.MiterJoin)

class NodeOpGroup(QtGui.QGraphicsItemGroup):

    def __init__(self, controller, function, scene=None, parent=None):
        QtGui.QGraphicsItemGroup.__init__(self,scene=scene, parent=parent)
        self.controller = controller
        self.compiled = None
        self.title = ""
        
        self.operator = NodeOp(scene)
        self.addToGroup(self.operator)
        
        self.inputPivot = (self.boundingRect().width()/2,0)
        self.inputs = []
        self.outputs = []
        self.connections = []
        
        
        self.outport = Output(scene)
        self.addToGroup(self.outport)
        self.outport.setPos(45,40)

    	self.setFlag(QtGui.QGraphicsItem.ItemIsMovable, True);
    	self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable, True);
    	self.setHandlesChildEvents(False)
        
        self.func = NodeOps.Engine.getFuncObj(function)
        self.initFuncAttrs()
        self.updateInputConn(QtCore.QPointF(0,0))

    def initFuncAttrs(self):
        #Set Node Title
        typeCount = 0
        for node in self.controller.nodes:
            if node.func.func_name == self.func.func_name:
                typeCount += 1
        self.title = QtGui.QGraphicsTextItem(self.func.func_name+ "_%s"%typeCount)
        self.addToGroup(self.title)
        
        #Create appropriate inputs
        for i in range(self.func.func_code.co_argcount):
            self.addInput()

    def setTitle(self,title):
        self.title.setPlainText(title)
        
    def delete(self):
        self.scene().removeItem(self)
        for conn in self.inputs:
            self.scene().removeItem(conn)
        for conn in self.outputs:
            conn.connected = False
            conn.node.updateInputConn(QtCore.QPointF(0,0))
            self.outputs.remove(conn)
            
        self.controller.nodes.remove(self)
        
    def connectInput(self,node,idx):
        self.inputs[idx].connected = True
        self.inputs[idx].dragged = True
        node.outputs.append(self.inputs[idx])
        scenePos= self.scene().views()[0].mapToScene(node.outport.pos().x(),
                                       node.outport.pos().y())
        
        x2 = node.outport.scenePos().x()+(node.outport.boundingRect().width()/2)
        y2 = node.outport.scenePos().y()+(node.outport.boundingRect().height()/2)

        self.updateInputConn(QtCore.QPointF(x2,y2))
        self.inputs[idx].dragged = False
        

    def updateInputConn(self, position):
        for input in self.inputs:
            x1 = self.pos().x() + self.inputPivot[0]
            y1 = self.pos().y() + self.inputPivot[1]

            if not input.connected:
                x2 = self.pos().x() + input.offset[0]
                y2 = self.pos().y() + input.offset[1]
            else:
                x2 = input.line().x2()
                y2 = input.line().y2()

            if input.dragged:
                x2 = position.x()
                y2 = position.y()

                
            line = QtCore.QLineF(x1,y1,x2,y2)
            input.setLine(line)
            
        for output in self.outputs:
            if output.connected:
                x1 = output.line().x1()
                y1 = output.line().y1()
                scenePos= self.scene().views()[0].mapToScene(self.outport.pos().x(),
                                                       self.outport.pos().y())
                x2 = self.outport.scenePos().x()+(self.outport.boundingRect().width()/2)
                y2 = self.outport.scenePos().y()+(self.outport.boundingRect().height()/2)
                output.setLine(QtCore.QLineF(x1,y1,x2,y2))
            else:
                self.outputs.remove(output)
    
    def updateOutputConn(self,outputWidget,position):
        idx = self.outputs.index(outputWidget)

    def addInput(self):
        inputWidget = ConnLine(self) 
        inputWidget.setZValue(-1000)
        self.scene().addItem(inputWidget)
        self.inputs.append(inputWidget)
        spread = len(self.inputs)*5
        center = self.boundingRect().width()/2
        start = center - spread
        for input in self.inputs:
            if len(self.inputs) % 2 == 0:
                if start == center:
                    start += spread
                    input.offset = (start,-20)
                start += spread
            else:
                input.offset = (start,-20)
                start += spread


    def connectOutput(self,outputWidget):
        self.outputs.append(outputWidget)
        
        
class NodeOp(QtSvg.QGraphicsSvgItem):

    def __init__(self, scene=None):
    	QtSvg.QGraphicsSvgItem.__init__(self,
					"./resources/NodeOp.svg")
        self.setElementId("NodeOp")
    	self.setFlag(QtGui.QGraphicsItem.ItemIsMovable, True);
    	self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QtGui.QGraphicsItem.ItemIsFocusable, True)

    def mouseMoveEvent(self,event):
    	QtSvg.QGraphicsSvgItem.mouseMoveEvent(self,event)
        self.group().updateInputConn(event.scenePos())
        #self.group().updateOutputConn(self,event.pos())
        
                
    def mouseReleaseEvent(self,event):  
        QtSvg.QGraphicsSvgItem.mouseReleaseEvent(self,event)
        
        
    def keyPressEvent(self,event):
        if event.key() == 16777219:
            self.group().delete()
    
class Output(QtSvg.QGraphicsSvgItem):

    def __init__(self,scene=None,parent=None):
        QtSvg.QGraphicsSvgItem.__init__(self,
                    "./resources/NodeOp.svg")
    
        self.setElementId("output")
        if scene:
            scene.addItem(self)
    
    
class ConnLine(QtGui.QGraphicsLineItem):
    
    def __init__(self, node, parent=None):
        #self.node is the parent node
        self.node = node
        self.offset = (40,-20)
        line = QtCore.QLineF(self.node.boundingRect().width()/2,
                             self.node.boundingRect().height()/2,*self.offset)
        QtGui.QGraphicsLineItem.__init__(self,line,parent=None)
        brush = QtGui.QColor(0,0,0)
        pen = QtGui.QPen(QtGui.QColor(0,0,0),4,
                    Qt.SolidLine,Qt.FlatCap,Qt.MiterJoin)
        self.setPen(pen)
        self.setLine(line)
        #self.setFlag(QtGui.QGraphicsItem.ItemIsMovable, True);
        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable, True);
        self.connected = False
        self.dragged = False
        
        
    def mouseMoveEvent(self,event):
        QtGui.QGraphicsLineItem.mouseMoveEvent(self,event)
        self.dragged = True
        self.connected = False
        self.node.updateInputConn(event.scenePos())

    def mouseReleaseEvent(self,event):
        QtGui.QGraphicsLineItem.mouseReleaseEvent(self,event)
        self.dragged = False
        
        targetWidget = self.scene().items(event.scenePos())
        if targetWidget:
            if isinstance(targetWidget[0],Output) and targetWidget[0] != self.node or\
               isinstance(targetWidget[0],NodeOp) and targetWidget[0].group() != self.node:
                self.connected = True
                x2 = targetWidget[0].pos().x()+(targetWidget[0].group().outport.boundingRect().width()/2)
                y2 = targetWidget[0].pos().y()+(targetWidget[0].group().outport.boundingRect().height()/2)
                self.line().setP2(QtCore.QPointF(x2,y2))
                targetWidget[0].group().connectOutput(self)
                
        self.node.updateInputConn(event.scenePos())
