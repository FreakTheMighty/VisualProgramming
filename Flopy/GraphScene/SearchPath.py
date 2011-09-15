from PyQt4 import QtGui, QtCore
import os

class SearchPaths(QtCore.QAbstractListModel):

    def __init__(self):
        QtCore.QAbstractListModel.__init__(self)
        self._paths = []

    def headerData(self, section, orientation, role):

        if role == QtCore.Qt.DisplayRole:

            if orientation == QtCore.Qt.Horizontal:
                return QtCore.QString("Search Paths")
            else:
                return QtCore.QString("Path")

    def rowCount(self,parent):
        return len(self._paths)

    def data(self, index, role):

        if role == QtCore.Qt.EditRole:
            return self._paths[index.row()]

        if role == QtCore.Qt.DisplayRole:
            row = index.row()
            value = self._paths[row]
            return value

    def setData(self, index, value, role = QtCore.Qt.EditRole):
        if role == QtCore.Qt.EditRole:
            row = index.row()
            self._paths[row] = value
            self.dataChanged.emit(index, index)
            return True
        return False
            
    def flags(self, index):
        return QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def insertRow(self, position, path, parent = QtCore.QModelIndex()):
        self.beginInsertRows(parent,position,position -1)
        self._paths.insert(position,path)
        self.endInsertRows()
        return True

    def removeRow(self, position, path, parent = QtCore.QModelIndex()):
        self.beginRemoveRows(parent, position, position - 1)
        self._paths.remove(path)
        self.endRemoveRows()
        return True


class SearchPathView(QtGui.QListView):

    def __init__(self,parent=None):
        QtGui.QListView.__init__(self,parent=parent)
        self.setModel(SearchPaths())
        self.setItemDelegateForColumn(0,PathFinder(self))


class PathFinder(QtGui.QItemDelegate):

    def __init__(self, parent=None):
        QtGui.QItemDelegate.__init__(self, parent)
        dirname = os.path.dirname(os.getcwd())
        subdirs = os.listdir(dirname)
        fulldirs = [os.path.join(dirname,s) for s in subdirs]
        self.completer = QtGui.QCompleter(fulldirs,self)
        self.lineEdit = None

    def createEditor(self, parent, option, index):
        self.lineEdit = QtGui.QLineEdit(parent)
        self.lineEdit.setCompleter(self.completer)
        self.lineEdit.textChanged.connect(self.updateCompleter)
        return self.lineEdit

    def updateCompleter(self,text):
        try:
            dirname = os.path.dirname(str(text))
            subdirs = os.listdir(dirname)
            fulldirs = [os.path.join(dirname,s) for s in subdirs]
            self.completer = QtGui.QCompleter(fulldirs,self)
            self.lineEdit.setCompleter(self.completer)
        except OSError:
            print 'no such directory'


class SearchPathDialog(QtGui.QDialog):

    def __init__(self,parent=None):
        QtGui.QDialog.__init__(self,parent=parent)
        self.layout = QtGui.QVBoxLayout()
        self.setLayout(self.layout)
        self.addButton = QtGui.QPushButton("Add")
        self.layout.addWidget(self.addButton)
        self.view = SearchPathView(parent=self)
        self.layout.addWidget(self.view)
        self.addButton.clicked.connect(self.addPath)

    def addPath(self,checked):
        self.view.model().insertRow(0,os.getcwd())
