from PyQt4 import QtCore, QtGui
import editor
import runner

class EditWidget(QtCore.QObject):

    def __init__(self,parent=None):
        QtCore.QObject.__init__(self,parent=parent)
        self.editor = editor.Ui_editor()
        self.editor.setupUi(parent)
        self.runner = runner.ThreadedRunner(self)
        self.editor.Input.codeLineEntered.connect(self.runner.codeSignal)
        self.editor.Input.moveHistory.connect(self.runner.cycleHistory)
        self.runner.codeResult.connect(self.editor.Output.append)
        self.runner.codeHistory.connect(self.editor.Input.setColorizedText)
        self.codeThreads = [QtCore.QThread()]
        self.runner.moveToThread(self.codeThreads[-1])
        self.codeThreads[-1].start()
