import math

from PyQt4 import QtGui
from PyQt4 import QtCore
import networkx


class GraphScene(QtGui.QGraphicsScene):

    def __init__(self,graph,*args,**kwargs):
        QtGui.QGraphicsScene.__init__(self,*args,**kwargs)
        self.graph = graph
        self.oploader = None
        self.loaderproxy = None
        self.nodeItems = []
        self.edgeItems = []
        self.mode = "dragging"
        #The current edge is the line that is being dragged
        self.currentedge= None

    def keyPressEvent(self,keyevent):

        #Replace with constants.
        if keyevent.key()  == 32:
            pos = self.views()[0].mapToScene(self.views()[0].mapFromGlobal(QtGui.QCursor().pos()))
            if not self.loaderproxy:
                self.loaderproxy = self.addWidget(self.oploader)
            else:
                self.loaderproxy.show()
            self.loaderproxy.setPos(pos.x(),pos.y())
        elif keyevent.key() == 16777220:
            self.loaderproxy.hide()
            self.emit(QtCore.SIGNAL("addNode(QString)"),self.loaderproxy.widget().currentText())
        QtGui.QGraphicsScene.keyPressEvent(self,keyevent)


    def findEdgeItem(self,nodeItem,keyword):
        #Get all the arrows in the scene
        arrows = filter(lambda item: isinstance(item,Arrow) ,self.items())

        #Get all the arrows connected to this node with the specified keyword label
        arrows = filter(lambda arrow: arrow.endItem == nodeItem or arrow.startItem == nodeItem,arrows)
        arrows = filter(lambda arrow:arrow.keyword == keyword,arrows)
        return arrows

    def addEdge(self,node1,node2,pos,add_to_graph=True):
        nodeItem1 = self.nodeItem(node1)
        nodeItem2 = self.nodeItem(node2)

        if not nodeItem1:
            nodeItem1 = self.addNode(node1)
        if not nodeItem2:
            nodeItem2 = self.addNode(node2)
        
        try:
            arrow = self.findEdgeItem(nodeItem2,pos)[0]
        except IndexError, e:
            raise ValueError("Failed to connect input %s to %s. %s has %s inputs." % (pos,nodeItem2,nodeItem2,nodeItem2.node.in_count))
        arrow.startItem = nodeItem1
        arrow.endItem = nodeItem2
        if add_to_graph and not self.graph.has_edge(node1,node2,key=pos):
            self.graph.add_edge(node1,node2,key=pos)


    def addNode(self,node):
        if not node in self.graph.nodes():
            self.graph.add_node(node)
        nodeItem = NodeItemGroup(node,self.graph)
        if node not in self.nodeItems:
            self.nodeItems.append(nodeItem)
        for idx in range(node.in_count):
            arrow = Arrow(None,nodeItem,idx)
            self.addItem(arrow)
        arrow = Arrow(nodeItem,None,"")
        self.addItem(arrow)
        self.addItem(nodeItem)
        nodeItem.setPos(*node.pos)
        return nodeItem

    def addGraph(self,graph):
        self.graph = graph
        for node in self.graph.nodes():
            self.addNode(node)
        for node1, node2 in self.graph.edges():
            print self.graph.edge[node1][node2]
            for edge in self.graph.edge[node1][node2]:
                self.addEdge(node1,node2,edge,add_to_graph=False)


    def nodeItem(self,node):
        for nodeItem in self.nodeItems:
            if node == nodeItem.node:
                return nodeItem
        return None

    def edgeItem(self,node1,node2):
        return (self.nodeItem(node1),
                self.nodeItem(node2))

class NodeItemGroup(QtGui.QGraphicsItemGroup):

    def __init__(self,node, graph):
        QtGui.QGraphicsItemGroup.__init__(self)
        self.body = QtGui.QGraphicsPolygonItem()
        polygon = QtGui.QPolygonF(QtCore.QRectF(-40,-20,80,40))
        self.body.setPolygon(polygon)
        self.body.setBrush(QtGui.QBrush(QtGui.QColor(255,255,255,255)))
        self.addToGroup(self.body)
        text = QtGui.QGraphicsSimpleTextItem(node.name)
        text.setPos(-40,-20)
        self.addToGroup(text)
        self.node = node
        self.graph = graph
        self.argCount = 2
        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable, True);

    def __str__(self):
        return self.node.name

    def setPos(self,x,y):
        QtGui.QGraphicsItem.setPos(self,x,y)

    def acceptsInputs(self):
        if len(self.scene().graph.in_edges(self.node)) < self.argCount:
            return True
        else:
            return False

    def mouseMoveEvent(self,event):
        QtGui.QGraphicsItemGroup.mouseMoveEvent(self,event)

    def mouseReleaseEvent(self,event):
        QtGui.QGraphicsItemGroup.mouseReleaseEvent(self,event)
        self.node.pos = [self.pos().x(),self.pos().y()]
        networkx.write_yaml(self.graph,"/tmp/test.yaml")

class Arrow(QtGui.QGraphicsLineItem):
    
    def __init__(self,startItem,endItem,keyword,*args,**kwargs):
        QtGui.QGraphicsLineItem.__init__(self,*args,**kwargs)
        self.setZValue(-100)
        self.keyword = keyword
        self.setToolTip(str(self.keyword))
        self.arrowHead = QtGui.QPolygonF()
        self.startItem = startItem
        self.endItem = endItem
        self.color = QtGui.QColor(0)
        self.startPos = None
        self.endPos = None


    def __repr__(self):
        return "<%s-->%s [%s] object at %s>" % (str(self.startItem),str(self.endItem),self.keyword, id(self))

    def boundingRect(self):
        extra = (self.pen().width() + 20) / 2.0
        return QtCore.QRectF(self.line().p1(), QtCore.QSizeF(self.line().p2().x() - self.line().p1().x(),
                            self.line().p2().y() - self.line().p1().y())).normalized().adjusted(-extra,-extra,extra,extra)

    def shape(self):
        path = QtGui.QGraphicsLineItem.shape(self)
        path.addPolygon(self.arrowHead)
        return path

    def updatePosition(self):
        pass

    def mousePressEvent(self,event):
        pass

    def mouseMoveEvent(self,event):
        #If the edge does not have an end item than we are dragging it from the arrow
        if self.endItem:
            self.startPos = event.pos()
        elif self.startItem:
            self.endPos = event.pos()
        self.update()

    def mouseReleaseEvent(self,event):
        items = self.scene().items(event.pos())
        node = None
        for item in items:
            if isinstance(item,NodeItemGroup):
                node = item
                break
        #If the edge has an end item than it is an incoming edge and we're grabbing it from the tail
        if self.endItem:
            if node:
                self.startItem = node
                self.scene().graph.add_edge(self.startItem.node,self.endItem.node,key=self.keyword)
            else:
                if self.startItem:
                    if self.scene().graph.has_edge(self.startItem.node,self.endItem.node,key=self.keyword):
                        self.scene().graph.remove_edge(self.startItem.node,self.endItem.node,key=self.keyword)
                self.startItem = None

        #If the edge has a start item than we are dragging it from the arrow
        elif self.startItem:
            if node:
                #Get all the arrows in the scene
                arrows = filter(lambda item: isinstance(item,Arrow) ,self.scene().items())
                #Get all the arrows connected to this node without an input
                inputArrows = filter(lambda arrow: arrow.endItem == node and arrow.startItem == None,arrows)
                if inputArrows:
                    #Sort the arrows by their keywords, the first available arrow is what we'll connect to
                    inputArrows.sort(key=lambda obj: obj.keyword)
                    inputArrows[0].startItem = self.startItem
                    self.scene().graph.add_edge(self.startItem.node,node.node,key=inputArrows[0].keyword)
            else:
                if self.startItem and self.endItem:
                    if (self.startItem.node,self.endItem.node) in self.scene().graph.edges():
                        self.scene().graph.remove_edge(self.startItem.node,self.endItem.node,key=self.keyword)
                self.endItem = None
        self.startPos, self.endPos = None,None
        self.update()

    def paint(self,painter,option,widget):

        arrowSize = 15

        if self.startItem == None:
            if not self.startPos:
                #Get all the arrows in the scene
                arrows = filter(lambda item: isinstance(item,Arrow) ,self.scene().items())
                #Get all the arrows connected to this node without an input
                inputArrows = filter(lambda arrow: arrow.endItem == self.endItem and arrow.startItem == None,arrows)
                idx = (inputArrows.index(self)+1)*1.2
                startPos = self.endItem.pos()+QtCore.QPointF(-20*idx,-60)
            else:
                startPos = self.startPos
            endPos = self.endItem.pos()
        elif self.endItem == None:
            startPos = self.startItem.pos()
            if not self.endPos:
                endPos = startPos + QtCore.QPointF(0,30)
            else:
                endPos = self.endPos
        elif self.startItem and self.endItem:
            if self.startItem.collidesWithItem(self.endItem):
                return
            if not self.startPos:
                startPos = self.startItem.pos()
            else:
                startPos = self.startPos
            endPos = self.endItem.pos()
        else:
            return

        centerLine = QtCore.QLineF(startPos,endPos)

        if self.endItem:
            endPolygon = self.endItem.body.polygon()
            p1 = endPolygon.first() + endPos

            for i in range(endPolygon.count()+1):
                p2 = endPolygon.at(i) + self.endItem.pos()
                polyLine = QtCore.QLineF(p1,p2)
                intersectPoint = QtCore.QPointF()
                intersectType = polyLine.intersect(centerLine,intersectPoint)
                if intersectType == QtCore.QLineF.BoundedIntersection: break
                p1 = p2

            self.setLine(QtCore.QLineF(intersectPoint,startPos))
        else:
            self.setLine(QtCore.QLineF(endPos,startPos))

        angle = math.acos(self.line().dx()/self.line().length())
        angle = (math.pi * 2)-angle
        if self.line().dy()<0:
            angle = -angle
        arrowP1 = self.line().p1() + QtCore.QPointF(math.sin(angle+math.pi/3.0) * arrowSize,
                                            math.cos(angle + math.pi/3) * arrowSize)
        arrowP2 = self.line().p1() + QtCore.QPointF(math.sin(angle + math.pi - math.pi / 3) * arrowSize,
                                             math.cos(angle + math.pi - math.pi / 3) * arrowSize)
        

        self.arrowHead.clear()
        self.arrowHead.insert(0,self.line().p1())
        self.arrowHead.insert(1,arrowP1)
        self.arrowHead.insert(2,arrowP2)


        line = self.line()
        middle = (arrowP1+arrowP2)/2.0
        line.setP1(middle)

        pen = QtGui.QPen(self.color,4)
        painter.setPen(pen)
        painter.setBrush(self.color)
        painter.drawLine(line)

        pen = QtGui.QPen(self.color,1)
        painter.setPen(pen)
        painter.drawPolygon(self.arrowHead)

class OpLoader(QtGui.QComboBox):

    def __init__(self,graphscene, parent=None):
        QtGui.QComboBox.__init__(self,parent)
        self.graphscene = graphscene
        self.setEditable(True)



class OperatorsModel(QtCore.QAbstractListModel):

    def __init__(self,parent=None):
        QtCore.QAbstractListModel.__init__(self,parent)
        self.operators = []

    def rowCount(self,parent):
        return len(self.operators)

    def data(self,idx,displayroll):
        if displayroll == QtCore.Qt.DisplayRole:
            return self.operators[idx.row()].name

        elif displayroll == QtCore.Qt.EditRole:
            return self.operators[idx.row()].name

