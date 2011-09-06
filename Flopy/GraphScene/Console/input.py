from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import QObject, pyqtSignal

class CodeInput(QtGui.QTextEdit):

    codeLineEntered = pyqtSignal("QString")
    moveHistory = pyqtSignal(int)

    def __init__(self,parent=None):
        QtGui.QTextEdit.__init__(self,parent)

    def keyPressEvent(self,event):
        QtGui.QTextEdit.keyPressEvent(self,event)
        if event.key() == 16777220:
            line = self.toPlainText()
            line = str(line).strip("\n")
            self.codeLineEntered.emit(line)
            self.setPlainText("")
        elif event.key() == 16777235:
            self.moveHistory.emit(1)
        elif event.key() == 16777237:
            self.moveHistory.emit(-1)
