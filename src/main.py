import sys
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtCore import QThread, QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import uic
import pyqtgraph as pg
from pyqtgraph import PlotWidget
import numpy as np

from server import TcpServer

import settings


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        # Load QtDesigner file
        uic.loadUi("gpt_gui.ui", self)

        x = np.linspace(0, 100, 101)
        y = np.ones(101)

        # TODO: Set icon
        # self.setWindowIcon(QtGui.QIcon('im.png'))

        # Initialise data buffers
        self.V1_buffer = []
        self.V2_buffer = []
        self.V3_buffer = []
        self.I1_buffer = []
        self.I2_buffer = []
        self.I3_buffer = []

        self.plotGraphicsView.setBackground(settings.plot_background)
        self.line1 = self.plotGraphicsView.plot(
            self.V1_buffer, skipFiniteCheck=True, pen=settings.line1_color
        )
        self.line2 = self.plotGraphicsView.plot(
            self.V2_buffer, skipFiniteCheck=True, pen=settings.line2_color
        )
        self.line3 = self.plotGraphicsView.plot(
            self.V3_buffer, skipFiniteCheck=True, pen=settings.line3_color
        )

        # -------------
        # QThread setup
        # -------------
        # Create worker objects
        self.server = TcpServer(
            V1_buffer=self.V1_buffer,
            V2_buffer=self.V2_buffer,
            V3_buffer=self.V3_buffer,
            I1_buffer=self.I1_buffer,
            I2_buffer=self.I2_buffer,
            I3_buffer=self.I3_buffer,
        )

        # Create QThread objects
        self.receiveThread = QThread()

        # Move worker to threads
        self.server.moveToThread(self.receiveThread)

        # Connect thread signals
        self.receiveThread.started.connect(self.server.run_server)

        # Start threads
        self.receiveThread.start()

        # ------------
        # QTimer setup
        # ------------
        # Create timers
        self.plot_timer = QTimer()

        # Connect timer signals
        self.plot_timer.timeout.connect(self.update_plot)

        # Start timers
        self.plot_timer.start(100)

    def update_plot(self):
        # Process events after every plot operation to keep GUI responsive
        self.line1.setData(self.V1_buffer)
        QApplication.processEvents()

        self.line2.setData(self.V2_buffer)
        QApplication.processEvents()

        self.line3.setData(self.V3_buffer)
        QApplication.processEvents()


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
