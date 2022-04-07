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

        self.plotGraphicsView.setBackground(settings.plot_background)
        self.line1 = self.plotGraphicsView.plot(
            [], [], skipFiniteCheck=True, pen=settings.line1_color
        )
        self.line2 = self.plotGraphicsView.plot(
            [], [], skipFiniteCheck=True, pen=settings.line2_color
        )
        self.line3 = self.plotGraphicsView.plot(
            [], [], skipFiniteCheck=True, pen=settings.line3_color
        )

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
        # Process events after every plotting event to keep GUI responsive

        # Check which plot type is selected in combo box then display the lines
        # corresponding to selected check boxes.
        combo_box_current_index = self.plotTypeComboBox.currentIndex()

        if combo_box_current_index == settings.V_combo_box_index:
            if self.line1CheckBox.isChecked():
                self.server.mutex.lock()
                self.line1.setData(self.server.V1_buffer[self.server.V1_lower_limit:self.server.V1_upper_limit])
                self.server.mutex.unlock()
            else:
                self.line1.setData([], [])
            QApplication.processEvents()

            if self.line2CheckBox.isChecked():
                self.server.mutex.lock()
                self.line2.setData(self.server.V2_buffer[self.server.V2_lower_limit:self.server.V2_upper_limit])
                self.server.mutex.unlock()
            else:
                self.line2.setData([], [])
            QApplication.processEvents()

            if self.line3CheckBox.isChecked():
                self.server.mutex.lock()
                self.line3.setData(self.server.V3_buffer[self.server.V3_lower_limit:self.server.V3_upper_limit])
                self.server.mutex.unlock()
            else:
                self.line3.setData([], [])
            QApplication.processEvents()

        elif combo_box_current_index == settings.I_combo_box_index:
            if self.line1CheckBox.isChecked():
                self.server.mutex.lock()
                self.line1.setData(self.server.I1_buffer[self.server.I1_lower_limit:self.server.I1_upper_limit])
                self.server.mutex.unlock()
            else:
                self.line1.setData([], [])
            QApplication.processEvents()

            if self.line2CheckBox.isChecked():
                self.server.mutex.lock()
                self.line2.setData(self.server.I2_buffer[self.server.I2_lower_limit:self.server.I2_upper_limit])
                self.server.mutex.unlock()
            else:
                self.line2.setData([], [])
            QApplication.processEvents()

            if self.line3CheckBox.isChecked():
                self.server.mutex.lock()
                self.line3.setData(self.server.I3_buffer[self.server.I3_lower_limit:self.server.I3_upper_limit])
                self.server.mutex.unlock()
            else:
                self.line3.setData([], [])
            QApplication.processEvents()


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
