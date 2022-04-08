import sys
from PyQt5 import QtCore, QtGui, QtWidgets
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

        # x = np.linspace(0, 100, 101)
        # y = np.ones(101)

        # TODO: Set icon
        # self.setWindowIcon(QtGui.QIcon('im.png'))

        self.plotGraphicsView.setBackground(settings.plotBackground)
        self.plotGraphicsView.showGrid(x=True, y=True)
        self.line1 = self.plotGraphicsView.plot(
            [],
            [],
            skipFiniteCheck=True,
            pen=pg.mkPen(settings.line1_color, width=settings.penWidth),
        )
        self.line2 = self.plotGraphicsView.plot(
            [],
            [],
            skipFiniteCheck=True,
            pen=pg.mkPen(settings.line2_color, width=settings.penWidth),
        )
        self.line3 = self.plotGraphicsView.plot(
            [],
            [],
            skipFiniteCheck=True,
            pen=pg.mkPen(settings.line3_color, width=settings.penWidth),
        )

        # Disable autorange which causes the view to automatically auto-range whenever
        # its contents are changed
        # self.plotGraphicsView.disableAutoRange()

        # Scale axis to display correct values for each tick
        self.plotGraphicsView.getAxis("bottom").setScale(
            settings.axisScalingFactor
        )

        # -------------
        # QThread setup
        # -------------
        # Create worker objects
        self.server = TcpServer(
                                inputGroup1DoubleSpinBox_1=self.inputGroup1DoubleSpinBox_1,
                                inputGroup1DoubleSpinBox_2=self.inputGroup1DoubleSpinBox_2,
                                inputGroup1DoubleSpinBox_3=self.inputGroup1DoubleSpinBox_3,
                                inputGroup2DoubleSpinBox_1=self.inputGroup2DoubleSpinBox_1,
                                inputGroup2DoubleSpinBox_2=self.inputGroup2DoubleSpinBox_2,
                                inputGroup2DoubleSpinBox_3=self.inputGroup2DoubleSpinBox_3
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
        self.plotTimer = QTimer()
        self.measurementsTimer = QTimer()

        # Connect timer signals
        self.plotTimer.timeout.connect(self.update_plot)
        self.measurementsTimer.timeout.connect(self.updateMeasurements)

        # Start timers
        self.plotTimer.start(settings.plotRefreshRate)
        self.measurementsTimer.start(settings.measurementsRefreshRate)

        # --------------------
        # Emit initial signals
        # --------------------
        self.onPlotTypeComboBoxSelect(self.plotTypeComboBox.currentIndex())

    def onMeasurementsButtonClicked(self, isChecked):
        if isChecked:
            self.channel1Measurements.setHidden(False)
            self.channel2Measurements.setHidden(False)
            self.channel3Measurements.setHidden(False)

        else:
            self.channel1Measurements.setHidden(True)
            self.channel2Measurements.setHidden(True)
            self.channel3Measurements.setHidden(True)

    def updateMeasurements(self):
        comboBoxCurrentIndex = self.plotTypeComboBox.currentIndex()
        if comboBoxCurrentIndex == settings.V_combo_box_index:
            self.channel1Measurements.setText(f"f0_V1: {self.server.f0_V1:.3f} Hz")
            self.channel2Measurements.setText(f"f0_V2: {self.server.f0_V2:.3f} Hz")
            self.channel3Measurements.setText(f"f0_V3: {self.server.f0_V3:.3f} Hz")

        elif comboBoxCurrentIndex == settings.I_combo_box_index:
            self.channel1Measurements.setText(f"f0_I1: {self.server.f0_I1:.3f} Hz")
            self.channel2Measurements.setText(f"f0_I2: {self.server.f0_I2:.3f} Hz")
            self.channel3Measurements.setText(f"f0_I3: {self.server.f0_I3:.3f} Hz")

    def update_plot(self):
        # Process events after every plotting event to keep GUI responsive

        # Check which plot type is selected in combo box then display the lines
        # corresponding to selected check boxes.
        comboBoxCurrentIndex = self.plotTypeComboBox.currentIndex()

        if comboBoxCurrentIndex == settings.V_combo_box_index:
            if not self.historyButton.isChecked():
                if self.line1CheckBox.isChecked():
                    self.server.mutex.lock()
                    self.line1.setData(
                        self.server.V1_buffer[
                            self.server.V1_lower_limit : self.server.V1_upper_limit
                        ]
                    )
                    self.server.mutex.unlock()
                else:
                    self.line1.clear()
                QApplication.processEvents()

            if not self.historyButton.isChecked():
                if self.line2CheckBox.isChecked():
                    self.server.mutex.lock()
                    self.line2.setData(
                        self.server.V2_buffer[
                            self.server.V2_lower_limit : self.server.V2_upper_limit
                        ]
                    )
                    self.server.mutex.unlock()
                else:
                    self.line2.clear()
                QApplication.processEvents()

            if not self.historyButton.isChecked():
                if self.line3CheckBox.isChecked():
                    self.server.mutex.lock()
                    self.line3.setData(
                        self.server.V3_buffer[
                            self.server.V3_lower_limit : self.server.V3_upper_limit
                        ]
                    )
                    self.server.mutex.unlock()
                else:
                    self.line3.clear()
                QApplication.processEvents()

        elif comboBoxCurrentIndex == settings.I_combo_box_index:
            if not self.historyButton.isChecked():
                if self.line1CheckBox.isChecked():
                    self.server.mutex.lock()
                    self.line1.setData(
                        self.server.I1_buffer[
                            self.server.I1_lower_limit : self.server.I1_upper_limit
                        ]
                    )
                    self.server.mutex.unlock()
                else:
                    self.line1.clear()
                QApplication.processEvents()

            if not self.historyButton.isChecked():
                if self.line2CheckBox.isChecked():
                    self.server.mutex.lock()
                    self.line2.setData(
                        self.server.I2_buffer[
                            self.server.I2_lower_limit : self.server.I2_upper_limit
                        ]
                    )
                    self.server.mutex.unlock()
                else:
                    self.line2.clear()
                QApplication.processEvents()

            if not self.historyButton.isChecked():
                if self.line3CheckBox.isChecked():
                    self.server.mutex.lock()
                    self.line3.setData(
                        self.server.I3_buffer[
                            self.server.I3_lower_limit : self.server.I3_upper_limit
                        ]
                    )
                    self.server.mutex.unlock()
                else:
                    self.line3.clear()
                QApplication.processEvents()

    def zoomInX(self):
        s = settings.zoom_amount
        zoom = (s, 1)
        self.plotGraphicsView.getViewBox().scaleBy(zoom)

    def zoomOutX(self):
        s = settings.zoom_amount
        zoom = (1 / s, 1)
        self.plotGraphicsView.getViewBox().scaleBy(zoom)

    def zoomInY(self):
        s = settings.zoom_amount
        zoom = (1, s)
        self.plotGraphicsView.getViewBox().scaleBy(zoom)

    def zoomOutY(self):
        s = settings.zoom_amount
        zoom = (1, 1 / s)
        self.plotGraphicsView.getViewBox().scaleBy(zoom)

    def onHistoryButtonClicked(self, isChecked):
        # Before plotting, disable autoranging
        if self.historyButton.isChecked():
            self.plotGraphicsView.disableAutoRange()
            self.server.mutex.lock()
            self.plotGraphicsView.setXRange(len(self.server.V1_buffer)-settings.nSamplesInView, len(self.server.V1_buffer), padding=0)
            self.server.mutex.unlock()
        else:
            self.plotGraphicsView.enableAutoRange()

        comboBoxCurrentIndex = self.plotTypeComboBox.currentIndex()

        if comboBoxCurrentIndex == settings.V_combo_box_index:
            if isChecked == True:
                if self.line1CheckBox.isChecked():
                    self.line1.setData(self.server.V1_buffer, clipToView=True)
                else:
                    self.line1.clear()
                QApplication.processEvents()

            if isChecked == True:
                if self.line2CheckBox.isChecked():
                    self.line2.setData(self.server.V2_buffer, clipToView=True)
                else:
                    self.line2.clear()
                QApplication.processEvents()

            if isChecked == True:
                if self.line3CheckBox.isChecked():
                    self.line3.setData(self.server.V3_buffer, clipToView=True)
                else:
                    self.line3.clear()
                QApplication.processEvents()

        elif comboBoxCurrentIndex == settings.I_combo_box_index:
            if isChecked == True:
                if self.line1CheckBox.isChecked():
                    self.line1.setData(self.server.I1_buffer, clipToView=True)
                else:
                    self.line1.clear()
                QApplication.processEvents()

            if isChecked == True:
                if self.line2CheckBox.isChecked():
                    self.line2.setData(self.server.I2_buffer, clipToView=True)
                else:
                    self.line2.clear()
                QApplication.processEvents()

            if isChecked == True:
                if self.line3CheckBox.isChecked():
                    self.line3.setData(self.server.I3_buffer, clipToView=True)
                else:
                    self.line3.clear()
                QApplication.processEvents()

            # Reset axis limits to avoid displaying too many points
            # setXRange(5, 20, padding=0)

        # Let update_plot handle the else so that there is no race condition

    def onPlotTypeComboBoxSelect(self, comboBoxCurrentIndex):
        if comboBoxCurrentIndex == settings.V_combo_box_index:
            self.line1CheckBox.setText("V1")
            self.line2CheckBox.setText("V2")
            self.line3CheckBox.setText("V3")

        elif comboBoxCurrentIndex == settings.I_combo_box_index:
            self.line1CheckBox.setText("I1")
            self.line2CheckBox.setText("I2")
            self.line3CheckBox.setText("I3")

    def onLine1CheckBoxClickedHistoryPlot(self):
        comboBoxCurrentIndex = self.plotTypeComboBox.currentIndex()

        if comboBoxCurrentIndex == settings.V_combo_box_index:
            if self.historyButton.isChecked():
                if self.line1CheckBox.isChecked():
                    self.line1.setData(self.server.V1_buffer)
                else:
                    self.line1.clear()
                QApplication.processEvents()

        elif comboBoxCurrentIndex == settings.I_combo_box_index:
            if self.historyButton.isChecked():
                if self.line1CheckBox.isChecked():
                    self.line1.setData(self.server.I1_buffer)
                else:
                    self.line1.clear()
                QApplication.processEvents()

    def onLine2CheckBoxClickedHistoryPlot(self):
        comboBoxCurrentIndex = self.plotTypeComboBox.currentIndex()

        if comboBoxCurrentIndex == settings.V_combo_box_index:
            if self.historyButton.isChecked():
                if self.line2CheckBox.isChecked():
                    self.line2.setData(self.server.V2_buffer)
                else:
                    self.line2.clear()
                QApplication.processEvents()

        elif comboBoxCurrentIndex == settings.I_combo_box_index:
            if self.historyButton.isChecked():
                if self.line2CheckBox.isChecked():
                    self.line2.setData(self.server.I2_buffer)
                else:
                    self.line2.clear()
                QApplication.processEvents()

    def onLine3CheckBoxClickedHistoryPlot(self):
        comboBoxCurrentIndex = self.plotTypeComboBox.currentIndex()

        if comboBoxCurrentIndex == settings.V_combo_box_index:
            if self.historyButton.isChecked():
                if self.line3CheckBox.isChecked():
                    self.line3.setData(self.server.V3_buffer)
                else:
                    self.line3.clear()
                QApplication.processEvents()

        elif comboBoxCurrentIndex == settings.I_combo_box_index:
            if self.historyButton.isChecked():
                if self.line3CheckBox.isChecked():
                    self.line3.setData(self.server.I3_buffer)
                else:
                    self.line3.clear()
                QApplication.processEvents()


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
