import ctypes
import sys

from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog

import preRun
import customExceptions

qtCreatorFile = "baseUI.ui"
helpUI = "helpWindow.ui"
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)

alphabet = ""
inputString = ""
machineStates = ""
jTransitions = ""


class MainAppWindow(QMainWindow, Ui_MainWindow):

    def startAction(self):
        try:
            alphabet = preRun.filterMachineAlphabet(self.inputAlphabetText.toPlainText())
            inputString = self.inputStringText.toPlainText()
            machineStates = self.machineStatesText.toPlainText()
            jTransitions = self.jumpsDeclareText.toPlainText()
        except invalid:
            pass

    @staticmethod
    def exitAction():
        sys.exit(1)

    def __init__(self):
        QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.exitButton.clicked.connect(self.exitAction)
        self.startButton.clicked.connect(self.startAction)

        # Set alternative style
        app.setStyle("fusion")

        # Disable default exit button
        self.setWindowFlags(Qt.WindowTitleHint)

        # Set custom title to title bar
        self.setWindowTitle("JFA Simulator")

        # Set Custom icon to app title bar
        self.setWindowIcon(QIcon("Image_Content\JFA_icon.png"))

        # Set custom icon to app in taskbar
        # This is a workaround I found on stackoverflow
        # Works via AppUserModelsIDs. Apart from that, I have no idea how it works
        myappid = 'JFA.Sim'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainAppWindow()
    window.show()
    sys.exit(app.exec_())
