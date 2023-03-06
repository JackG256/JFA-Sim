import ctypes
import sys

from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtWidgets import QApplication, QMainWindow, QCheckBox, QLabel, QVBoxLayout, QWidget

from customExceptions import *
import preRun
import runLogicDET
# import assistFunctions

qtCreatorFile = "baseUI.ui"
helpUI = "helpWindow.ui"
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)


class MainAppWindow(QMainWindow, Ui_MainWindow):

    def startAction(self):
        try:
            # Get and filter inputs
            self.alphabet = preRun.filterMachineAlphabet(self.inputAlphabetText.toPlainText())
            self.inputString, self.formattedInputDict = preRun.filterInputString(self.inputStringText.toPlainText(),
                                                                                 self.alphabet)
            self.currentReadSymbol = self.inputString[0]
            # self.inputString = self.inputString[1:]

            # Code to get information about shortened string, works with symbol key-value dictionary
            # Get keys
            keys = list(dict.fromkeys(self.inputString))
            values = []
            for key in keys:
                # Get occurence values for each key
                values.append(self.formattedInputDict[key])

            formattedInputStrToPrint = ""
            # For each key, put key in output string, and get occurence value based on index of same key
            for key in keys:
                formattedInputStrToPrint += f"// {key} ^ {values[keys.index(key)]} "

            # Final string detail
            formattedInputStrToPrint += "//"

            # Get currently selected start and end states
            tmp = self.statesCombobox.currentText()
            if tmp != "No Selection":
                self.startState = tmp

            self.endStates = [checkbox.text() for checkbox in self.checkBoxList if checkbox.isChecked()]

            # Get and filter inputs
            self.machineStates, self.currentState = preRun.filterMachineStates(self.machineStatesText.toPlainText(),
                                                                               self.startState,
                                                                               self.endStates)

            self.jTransitions = preRun.filterJumpTransitions(self.jumpsDeclareText.toPlainText(),
                                                             self.alphabet,
                                                             self.machineStates)

            # If all passed, ensure the user
            self.statusText.setText("Passed!\n"
                                    "Machine has been loaded!")

            # Print formatted input string to text field
            self.outputStringTextFormatted.setText(formattedInputStrToPrint)

            # Debug print
            print(f"\nSpecified alphabet: {self.alphabet}\nSpecified input str: {self.inputString}\nSpecified states:"
                  f" {self.machineStates}\nSpecified starting state: {self.startState}\n"
                  f"Specified end states: {self.endStates}\nSpecified jumps: {self.jTransitions}")

            self.machineStarted = True

            # Loop to clear and remove all sublayouts in the instancesGrid layout
            while self.instancesGrid.count():
                # Get and check if item is a widget, if yes, delete it
                item = self.instancesGrid.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    # Get and check if item is a layout, if yes, remove all items from it
                    sublayout = item.layout()
                    if sublayout is not None:
                        while sublayout.count():
                            subitem = sublayout.takeAt(0)
                            subwidget = subitem.widget()
                            if subwidget is not None:
                                subwidget.deleteLater()

            # Generate labels for an instance of JFA
            self.labelString = QLabel(''.join(self.inputString))
            self.labelState = QLabel(f"Current state {self.startState}")

            self.labelJumps = QLabel(str(runLogicDET.findNextJumps(self.jTransitions,
                                                                   self.currentState,
                                                                   self.inputString)))

            self.labelString.setFont(QFont("Arial", 14, QFont.Bold))
            self.labelString.setAlignment(Qt.AlignCenter)
            self.labelString.setFixedSize(158, 20)

            self.labelState.setFont(QFont("Arial", 10, QFont.Bold))
            self.labelState.setAlignment(Qt.AlignCenter)
            self.labelState.setFixedSize(158, 17)

            self.labelJumps.setFont(QFont("Arial", 12, QFont.Bold))
            self.labelJumps.setAlignment(Qt.AlignCenter)
            self.labelJumps.setFixedSize(158, 134)

            # Create a layout object containing labels
            layout = QVBoxLayout()
            layout.addWidget(self.labelString)
            layout.addWidget(self.labelState)
            layout.addWidget(self.labelJumpsText)
            layout.addWidget(self.labelJumps)

            # Assign the layout object to a layout widget
            layoutWidget = QWidget()
            layoutWidget.setFixedSize(158, 201)
            layoutWidget.setLayout(layout)

            self.instancesGrid.addWidget(layoutWidget)

        # Except branch to catch all custom exceptions and print them to status field
        # Functions as feedback to user about incorrect input
        except (EmptyFieldError, InvalidAlphabetFormatError, InvalidSymbolInAlphabetError,
                InputSymbolNotInAlphabetError, StartStateNotFoundError, EndStateNotFoundError, StateDoesNotExistError,
                SymbolDoesNotExistError) as exc:
            self.statusText.setText(f"<b>ERROR</b><br><br>{exc}")

    @staticmethod
    def exitAction():
        sys.exit(1)

    def loadStatesAction(self):
        # Pull inputted states from text box and split them into a list
        states = self.machineStatesText.toPlainText().replace('\n', '').split(";")

        # Clear the selection combobox before assigning new values
        self.statesCombobox.clear()

        # Clear the list of checkboxes
        self.checkBoxList.clear()

        # Loop to remove all checkbox widgets
        for i in reversed(range(self.endStatesGrid.count())):
            # Get widget by index
            widget = self.endStatesGrid.itemAt(i).widget()
            if widget is not None:
                # Remove from layout
                self.endStatesGrid.removeWidget(widget)
                # Remove widget itself
                widget.deleteLater()

        # Default value assignment
        self.statesCombobox.addItem("No Selection")

        # Failsafe if empty text box
        if len(states) == 1 and states[0] == '':
            return False

        # Helping variables
        num_cols = 4
        row = 0
        col = 0

        # For each state in list
        for i, state in enumerate(states):
            if str(state) == "":
                continue

            # Add item to combobox
            self.statesCombobox.addItem(state)

            # Create a checkbox widget and assign it to the layout of checkboxes
            checkbox = QCheckBox(state)
            self.endStatesGrid.addWidget(checkbox, row, col)

            # Add instance of checkbox to global list
            self.checkBoxList.append(checkbox)
            col += 1
            if col == num_cols:
                col = 0
                row += 1

    def stepAction(self):
        if self.machineStarted:
            try:
                self.formattedInputDict, self.inputString, self.currentState, self.prevState = runLogicDET.findAndRunJumpOneSide(
                    self.jTransitions,
                    self.currentState,
                    self.machineStates,
                    self.formattedInputDict,
                    self.inputString)

                self.statusText.setText(f"A jump has been performed!\n{self.prevState[0]} -> {self.currentState}"
                                        f" via reading {self.prevState[1]}")

                print(f"\nA jump has been performed\nNew formatted string:")

                for key in self.formattedInputDict:
                    print(f"Key: '{key}': {self.formattedInputDict[key]}")

            except NoJumpToPerform as exc:
                self.statusText.setText(f"<b>ERROR</b><br><br>{exc}")

            print(f"\nNew input string: {self.inputString}" f"\nNew current state: {self.currentState}")

            if len(self.inputString) == 0:
                if self.currentState in self.endStates:
                    print("END! ACCEPTED")
                    self.statusText.setText(f"<b>Machine ACCEPTED</b><br>"
                                            f"A jump has been performed!<br>{self.prevState[0]} -> {self.currentState}"
                                            f" via reading {self.prevState[1]}")
                else:
                    self.statusText.setText(f"<b>Machine REFUSED</b><br>"
                                            f"A jump has been performed!<br>{self.prevState[0]} -> {self.currentState}"
                                            f" via reading {self.prevState[1]}")
                self.machineStarted = False

    def runToEndAction(self):
        while self.machineStarted:
            self.stepAction()

    def __init__(self):
        QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)

        self.machineStarted = False
        self.startState = ""
        self.endStates = []

        self.alphabet = ""
        self.inputString = ""
        self.machineStates = ""
        self.jTransitions = ""

        self.labelString = ""
        self.labelState = ""
        self.labelJumpsText = QLabel("Possible jumps\nfrom state:\n")
        self.labelJumps = ""

        self.labelJumpsText.setFont(QFont("Arial", 10, QFont.Bold))
        self.labelJumpsText.setAlignment(Qt.AlignCenter)
        self.labelJumpsText.setFixedSize(158, 30)

        self.currentReadSymbol = ""
        self.currentState = ""
        self.prevState = ""
        self.checkBoxList = []

        self.formattedInputDict = []

        self.exitButton.clicked.connect(self.exitAction)
        self.startButton.clicked.connect(self.startAction)
        self.stepButton.clicked.connect(self.stepAction)
        self.runToEndButton.clicked.connect(self.runToEndAction)

        # Connect load states action on text changed flag
        self.machineStatesText.textChanged.connect(self.loadStatesAction)

        # Defulat value in selection box on run
        self.statesCombobox.addItem("No Selection")

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
