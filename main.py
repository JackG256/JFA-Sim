import ctypes
import sys

from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow

from customExceptions import *
import preRun
import runLogicND

qtCreatorFile = "baseUI.ui"
helpUI = "helpWindow.ui"
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)


class MainAppWindow(QMainWindow, Ui_MainWindow):

    def startAction(self):
        try:
            # Get and filter inputs
            self.alphabet = preRun.filterMachineAlphabet(self.inputAlphabetText.toPlainText())
            self.inputString, formattedInputDict = preRun.filterInputString(self.inputStringText.toPlainText(),
                                                                            self.alphabet)
            self.currentReadSymbol = self.inputString[0]
            # self.inputString = self.inputString[1:]

            # Code to get information about shortened string, works with symbol key-value dictionary
            # Get keys
            keys = list(dict.fromkeys(self.inputString))
            values = []
            for key in keys:
                # Get occurence values for each key
                values.append(formattedInputDict[key])

            formattedInputStrToPrint = ""
            # For each key, put key in output string, and get occurence value based on index of same key
            for key in keys:
                formattedInputStrToPrint += f"// {key} -> {values[keys.index(key)]} "

            # Final string detail
            formattedInputStrToPrint += "//"

            # Get and filter inputs
            self.machineStates, self.currentState = preRun.filterMachineStates(self.machineStatesText.toPlainText())
            self.jTransitions = preRun.filterJumpTransitions(self.jumpsDeclareText.toPlainText(), self.alphabet,
                                                             self.machineStates)

            # If all passed, ensure the user
            self.statusText.setText("Passed!")

            # Print formatted input string to text field
            self.outputStringTextFormatted.setText(formattedInputStrToPrint)

            # Debug print
            print(f"\nSpecified alphabet: {self.alphabet}\nSpecified input str: {self.inputString}\nSpecified states:"
                  f" {self.machineStates}\nSpecified jumps: {self.jTransitions}")

            self.machineStarted = True

        # Except branch to catch all custom exceptions and print them to status field
        # Functions as feedback to user about incorrect input
        except (EmptyFieldError, InvalidAlphabetFormatError, InvalidSymbolInAlphabetError,
                InputSymbolNotInAlphabetError, StartStateNotFoundError, EndStateNotFoundError, StateDoesNotExistError,
                SymbolDoesNotExistError) as exc:
            self.statusText.setText(f"<b>ERROR</b><br><br>{exc}")

    @staticmethod
    def exitAction():
        sys.exit(1)

    def stepAction(self):
        if self.machineStarted:
            self.inputString, self.currentState = runLogicND.findAndRunJumpOneSide(self.jTransitions,
                                                                                   self.currentReadSymbol,
                                                                                   self.currentState,
                                                                                   self.machineStates,
                                                                                   self.inputString)

            print(f"\nA jump has been invoked\nNew input string: {self.inputString}"
                  f"\nNew current state: {self.currentState}")

            if len(self.inputString) == 0:
                if "!" + self.currentState in self.machineStates:
                    print("END! ACCEPTED")
                else:
                    print("END! REFUSED")
                self.machineStarted = False

    def runToEndAction(self):
        pass

    def __init__(self):
        QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)

        self.machineStarted = False
        self.startState = ""

        self.alphabet = ""
        self.inputString = ""
        self.machineStates = ""
        self.jTransitions = ""

        self.currentReadSymbol = ""
        self.currentState = ""

        self.exitButton.clicked.connect(self.exitAction)
        self.startButton.clicked.connect(self.startAction)
        self.stepButton.clicked.connect(self.stepAction)

        # Set alternative style
        app.setStyle("fusion")

        # Disable default exit button
        self.setWindowFlags(Qt.WindowTitleHint)

        # Set custom title to title bar
        self.setWindowTitle("JFA Simulator")

        # Set Custom icon to app title bar
        self.setWindowIcon(QIcon("Image_Content/JFA_icon.png"))

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
