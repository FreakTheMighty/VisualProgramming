#!/usr/bin/env python
import sys
from PyQt4.QtGui import QApplication
from Controller import GraphController

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GraphController()
    window.show()
    sys.exit(app.exec_())
