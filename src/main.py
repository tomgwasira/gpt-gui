import sys
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import uic
from pyqtgraph import PlotWidget
import numpy as np

from server import TcpServer


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        # Load QtDesigner file
        uic.loadUi("gpt_gui.ui", self)

        x = np.linspace(0, 100, 101)
        y = np.ones(101)

        self.plotGraphicsView.plot(x, y)

        # TODO: Set icon
        # self.setWindowIcon(QtGui.QIcon('im.png'))

        # -------------
        # QThread setup
        # -------------
        # Create worker objects
        self.server = TcpServer()

        # Create QThread objects
        self.receiveThread = QThread()

        # Move worker to threads
        self.server.moveToThread(self.receiveThread)

        # Connect thread signals
        self.receiveThread.started.connect(self.server.receive)
        self.server.dataReadyToPlot.connect(self.updatePlot)

        # Start threads
        self.receiveThread.start()

    def updatePlot(self):
        print("Signal to update received")


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
