from PyQt5.QtCore import QObject, pyqtSignal


class TcpServer(QObject):
    dataReadyToPlot = pyqtSignal()

    def receive(self):
        print("Receiving")
        self.dataReadyToPlot.emit()
