import sys
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setGeometry(0, 0, 800, 400)
        self.setWindowTitle("General Power Theory")
        # TODO: Set icon
        # self.setWindowIcon(QtGui.QIcon('im.png'))

        # self.mainWindow()

    # def mainWindow(self):
    #     self.quoteWindow = QuoteWindow()
    #     barMenu = QtWidgets.QTabWidget(self)
    #     tab1 = QtWidgets.QWidget()
    #     quoteLayout = QtWidgets.QVBoxLayout()
    #     quoteLayout.addWidget(self.quoteWindow)
    #     tab1.setLayout(quoteLayout)
    #     barMenu.addTab(tab1, "&Nueva Cotización")
    #     self.setCentralWidget(barMenu)


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
