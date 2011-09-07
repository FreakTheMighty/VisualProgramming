# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/coder.ui'
#
# Created: Mon Sep  5 23:07:19 2011
#      by: PyQt4 UI code generator 4.8.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_editor(object):
    def setupUi(self, editor):
        editor.setObjectName(_fromUtf8("editor"))
        editor.resize(443, 527)
        self.verticalLayout = QtGui.QVBoxLayout(editor)
        self.verticalLayout.setMargin(2)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.splitter = QtGui.QSplitter(editor)
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.setOpaqueResize(True)
        self.splitter.setHandleWidth(7)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.Output = QtGui.QTextEdit(self.splitter)
        self.Output.setReadOnly(True)
        self.Output.setObjectName(_fromUtf8("Output"))
        self.Input = CodeInput(self.splitter)
        self.Input.setObjectName(_fromUtf8("Input"))
        self.verticalLayout.addWidget(self.splitter)

        self.retranslateUi(editor)
        QtCore.QMetaObject.connectSlotsByName(editor)

    def retranslateUi(self, editor):
        editor.setWindowTitle(QtGui.QApplication.translate("editor", "Form", None, QtGui.QApplication.UnicodeUTF8))

from input import CodeInput
