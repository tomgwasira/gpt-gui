"""Graphical User Interface implementation for General Power Theory."""

# Standard library imports
import sys

# Third-party library imports
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QThread, QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import uic

import pyqtgraph as pg
from pyqtgraph import PlotWidget

import numpy as np

# Local application imports
import settings

from server import TcpServer

__author__ = "Thomas Gwasira"
__date__ = "March 2022"
__version__ = "0.1.0"
__email__ = "tomgwasira@gmail.com"
__status__ = "Development"


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        # Load QtDesigner file
        uic.loadUi("gpt_gui.ui", self)

        # ----------
        # Plot setup
        # ----------
        self.plotGraphicsView.setBackground(settings.plotBackground)
        self.plotGraphicsView.showGrid(x=True, y=True)
        self.line1 = self.plotGraphicsView.plot(
            [],
            [],
            skipFiniteCheck=True,
            pen=pg.mkPen(settings.line1Color, width=settings.penWidth),
        )
        self.line2 = self.plotGraphicsView.plot(
            [],
            [],
            skipFiniteCheck=True,
            pen=pg.mkPen(settings.line2Color, width=settings.penWidth),
        )
        self.line3 = self.plotGraphicsView.plot(
            [],
            [],
            skipFiniteCheck=True,
            pen=pg.mkPen(settings.line3Color, width=settings.penWidth),
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
        self.receiveThread.started.connect(self.server.runServer)

        # Start threads
        self.receiveThread.start()

        # ------------
        # QTimer setup
        # ------------
        # Create timers
        self.plotTimer = QTimer()
        self.measurementsTimer = QTimer()

        # Connect timer signals
        self.plotTimer.timeout.connect(self.updatePlot)
        self.measurementsTimer.timeout.connect(self.updateMeasurements)

        # Start timers
        self.plotTimer.start(settings.plotRefreshRate)
        self.measurementsTimer.start(settings.measurementsRefreshRate)

        # ----------------------
        # Widget initialisations
        # ----------------------
        self.onPlotTypeComboBoxSelect(self.plotTypeComboBox.currentIndex())

    def updatePlot(self):
        """Update plot widget.

        This method is called at regular intervals by a QTimer object.
        
        Data plotted for each buffer is just a slice of the buffer to reduce
        execution time of this function; hence, keeping the GUI responsive.
        Additionally, the slices are created in such a way as to implement the
        trigger function of an oscilloscope.

        After every line update, a call is made to QApplication.processEvents()
        to keep the GUI responsive.

        A mutex lock is used during every line update as certain variables used
        are shared with the server thread, therefore, this is required to prevent
        data races.
        """
        # Check which plot type is selected in combo box then display the lines
        # corresponding to selected check boxes.
        comboBoxCurrentIndex = self.plotTypeComboBox.currentIndex()

        if comboBoxCurrentIndex == settings.vComboBoxIndex:
            if not self.historyButton.isChecked():
                if self.line1CheckBox.isChecked():
                    self.server.mutex.lock()
                    self.line1.setData(
                        self.server.v1Buffer[
                            self.server.v1LowerLimit : self.server.v1UpperLimit
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
                        self.server.v2Buffer[
                            self.server.v2LowerLimit : self.server.v2UpperLimit
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
                        self.server.v3Buffer[
                            self.server.v3LowerLimit : self.server.v3UpperLimit
                        ]
                    )
                    self.server.mutex.unlock()
                else:
                    self.line3.clear()
                QApplication.processEvents()

        elif comboBoxCurrentIndex == settings.iComboBoxIndex:
            if not self.historyButton.isChecked():
                if self.line1CheckBox.isChecked():
                    self.server.mutex.lock()
                    self.line1.setData(
                        self.server.i1Buffer[
                            self.server.i1LowerLimit : self.server.i1UpperLimit
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
                        self.server.i2Buffer[
                            self.server.i2LowerLimit : self.server.i2UpperLimit
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
                        self.server.i3Buffer[
                            self.server.i3LowerLimit : self.server.i3UpperLimit
                        ]
                    )
                    self.server.mutex.unlock()
                else:
                    self.line3.clear()
                QApplication.processEvents()

    def updateMeasurements(self):
        """Update measurement labels.

        This method is called at regular intervals by a QTimer object.
        """
        comboBoxCurrentIndex = self.plotTypeComboBox.currentIndex()

        if comboBoxCurrentIndex == settings.vComboBoxIndex:
            self.channel1Measurements.setText(f"f0_V1: {self.server.f0_V1:.3f} Hz")
            self.channel2Measurements.setText(f"f0_V2: {self.server.f0_V2:.3f} Hz")
            self.channel3Measurements.setText(f"f0_V3: {self.server.f0_V3:.3f} Hz")

        elif comboBoxCurrentIndex == settings.iComboBoxIndex:
            self.channel1Measurements.setText(f"f0_I1: {self.server.f0_I1:.3f} Hz")
            self.channel2Measurements.setText(f"f0_I2: {self.server.f0_I2:.3f} Hz")
            self.channel3Measurements.setText(f"f0_I3: {self.server.f0_I3:.3f} Hz")

    def onPlotTypeComboBoxSelect(self, comboBoxCurrentIndex):
        """Handle any changes that need to be done to GUI elements when a different
        plot type is selected.
        """
        if comboBoxCurrentIndex == settings.vComboBoxIndex:
            self.line1CheckBox.setText("V1")
            self.line2CheckBox.setText("V2")
            self.line3CheckBox.setText("V3")

        elif comboBoxCurrentIndex == settings.iComboBoxIndex:
            self.line1CheckBox.setText("I1")
            self.line2CheckBox.setText("I2")
            self.line3CheckBox.setText("I3")

    def onHistoryButtonClicked(self, isChecked):
        """Plot buffers in their entirety rather than just slices when the
        history button is clicked.
        """
        if self.historyButton.isChecked():
            # Disable autorange before plotting
            self.plotGraphicsView.disableAutoRange()
            
            self.server.mutex.lock()
            self.plotGraphicsView.setXRange(len(self.server.v1Buffer)-settings.nSamplesInView, len(self.server.v1Buffer), padding=0)
            self.server.mutex.unlock()
        else:
            # Re-enable autorange if history button unchecked
            self.plotGraphicsView.enableAutoRange()

        comboBoxCurrentIndex = self.plotTypeComboBox.currentIndex()

        if comboBoxCurrentIndex == settings.vComboBoxIndex:
            if isChecked == True:
                if self.line1CheckBox.isChecked():
                    self.line1.setData(self.server.v1Buffer, clipToView=True)
                else:
                    self.line1.clear()
                QApplication.processEvents()

            if isChecked == True:
                if self.line2CheckBox.isChecked():
                    self.line2.setData(self.server.v2Buffer, clipToView=True)
                else:
                    self.line2.clear()
                QApplication.processEvents()

            if isChecked == True:
                if self.line3CheckBox.isChecked():
                    self.line3.setData(self.server.v3Buffer, clipToView=True)
                else:
                    self.line3.clear()
                QApplication.processEvents()

        elif comboBoxCurrentIndex == settings.iComboBoxIndex:
            if isChecked == True:
                if self.line1CheckBox.isChecked():
                    self.line1.setData(self.server.i1Buffer, clipToView=True)
                else:
                    self.line1.clear()
                QApplication.processEvents()

            if isChecked == True:
                if self.line2CheckBox.isChecked():
                    self.line2.setData(self.server.i2Buffer, clipToView=True)
                else:
                    self.line2.clear()
                QApplication.processEvents()

            if isChecked == True:
                if self.line3CheckBox.isChecked():
                    self.line3.setData(self.server.i3Buffer, clipToView=True)
                else:
                    self.line3.clear()
                QApplication.processEvents()

            # setXRange(5, 20, padding=0)

        # Let updatePlot handle the else so that there is no race condition

    def onLine1CheckBoxClickedHistoryPlot(self):
        """Display or hide line 1 when in history mode and the check button
        corresponding to the line is toggled.
        """
        comboBoxCurrentIndex = self.plotTypeComboBox.currentIndex()

        if comboBoxCurrentIndex == settings.vComboBoxIndex:
            if self.historyButton.isChecked():
                if self.line1CheckBox.isChecked():
                    self.line1.setData(self.server.v1Buffer)
                else:
                    self.line1.clear()
                QApplication.processEvents()

        elif comboBoxCurrentIndex == settings.iComboBoxIndex:
            if self.historyButton.isChecked():
                if self.line1CheckBox.isChecked():
                    self.line1.setData(self.server.i1Buffer)
                else:
                    self.line1.clear()
                QApplication.processEvents()

    def onLine2CheckBoxClickedHistoryPlot(self):
        """Display or hide line 2 when in history mode and the check button
        corresponding to the line is toggled.
        """
        comboBoxCurrentIndex = self.plotTypeComboBox.currentIndex()

        if comboBoxCurrentIndex == settings.vComboBoxIndex:
            if self.historyButton.isChecked():
                if self.line2CheckBox.isChecked():
                    self.line2.setData(self.server.v2Buffer)
                else:
                    self.line2.clear()
                QApplication.processEvents()

        elif comboBoxCurrentIndex == settings.iComboBoxIndex:
            if self.historyButton.isChecked():
                if self.line2CheckBox.isChecked():
                    self.line2.setData(self.server.i2Buffer)
                else:
                    self.line2.clear()
                QApplication.processEvents()

    def onLine3CheckBoxClickedHistoryPlot(self):
        """Display or hide line 3 when in history mode and the check button
        corresponding to the line is toggled.
        """
        comboBoxCurrentIndex = self.plotTypeComboBox.currentIndex()

        if comboBoxCurrentIndex == settings.vComboBoxIndex:
            if self.historyButton.isChecked():
                if self.line3CheckBox.isChecked():
                    self.line3.setData(self.server.v3Buffer)
                else:
                    self.line3.clear()
                QApplication.processEvents()

        elif comboBoxCurrentIndex == settings.iComboBoxIndex:
            if self.historyButton.isChecked():
                if self.line3CheckBox.isChecked():
                    self.line3.setData(self.server.i3Buffer)
                else:
                    self.line3.clear()
                QApplication.processEvents()


    def onMeasurementsButtonClicked(self, isChecked):
        """Display or hide measurements when the measurements button is
        clicked.
        """
        if isChecked:
            self.channel1Measurements.setHidden(False)
            self.channel2Measurements.setHidden(False)
            self.channel3Measurements.setHidden(False)

        else:
            self.channel1Measurements.setHidden(True)
            self.channel2Measurements.setHidden(True)
            self.channel3Measurements.setHidden(True)

    def zoomInX(self):
        """Zoom in x-axis."""
        s = settings.zoomAmount
        zoom = (s, 1)
        self.plotGraphicsView.getViewBox().scaleBy(zoom)

    def zoomOutX(self):
        """Zoom out x-axis."""
        s = settings.zoomAmount
        zoom = (1 / s, 1)
        self.plotGraphicsView.getViewBox().scaleBy(zoom)

    def zoomInY(self):
        """Zoom in y-axis."""
        s = settings.zoomAmount
        zoom = (1, s)
        self.plotGraphicsView.getViewBox().scaleBy(zoom)

    def zoomOutY(self):
        """Zoom out y-axis."""
        s = settings.zoomAmount
        zoom = (1, 1 / s)
        self.plotGraphicsView.getViewBox().scaleBy(zoom)

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
