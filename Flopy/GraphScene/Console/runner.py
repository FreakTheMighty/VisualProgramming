from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import QObject, pyqtSlot, pyqtSignal

import code
import sys

class ThreadedRunner(QtCore.QObject):

    codeResult = pyqtSignal("QString")
    codeHistory = pyqtSignal("QString")

    def __init__(self,editor):
        QtCore.QObject.__init__(self)
        self.editor = editor
        self.console = code.InteractiveConsole()
        self.stdout = WritableObject()
        self.history = []
        self.curline = 0

    @pyqtSlot("QString")
    def codeSignal(self,line):
        self.history.append(line)
        self.curline = len(self.history)
        sys.stdout = self.stdout
        try:
            self.console.runcode(str(line))
            sys.stdout = sys.__stdout__
            self.codeResult.emit(">>%s"%line)
            if len(self.stdout.content)>1:
                self.codeResult.emit("".join(self.stdout.content[:-1]))
            self.stdout.content = []
        except Exception, e:
            self.codeResult.emit(str(e))

    @pyqtSlot(int)
    def cycleHistory(self,delta):
        if (self.curline + delta) < len(self.history) and (self.curline + delta) >= 0:
            self.codeHistory.emit(self.history[self.curline+delta])
            self.curline += delta

class WritableObject:
    def __init__(self):
        self.content = []
    def write(self, string):
        self.content.append(string)


