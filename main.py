import ctypes
import sys
import os

from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QCheckBox,
    QLabel,
    QVBoxLayout,
    QWidget,
    QFileDialog,
)

from customExceptions import *
import preRun
import runLogicDET

# import assistFunctions

qtCreatorFile = "baseUI.ui"
helpUI = "helpWindow.ui"
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)

# Get options for file dialog
dialogOptions = QFileDialog.Options()
dialogOptions |= QFileDialog.DontUseNativeDialog

# Preset a path to the configs folder in documents
dialogDefaultDir = os.path.join(os.path.expanduser("~"), "Documents")
dialogDefaultDir = os.path.join(dialogDefaultDir, "JFA Configurations")
dialogDefaultFile = os.path.join(dialogDefaultDir, "JFA Configuration")


class MainAppWindow(QMainWindow, Ui_MainWindow):
    def saveConfigAction(self):
        # Check if default_dir exists, and create it if it doesn't
        if not os.path.exists(dialogDefaultDir):
            os.makedirs(dialogDefaultDir)

        # Open fileDialog
        filename, _ = QFileDialog.getSaveFileName(
            None,
            "Save Configuration File",
            dialogDefaultFile,
            "JFA Config Files (*.JFACON)",
            options=dialogOptions,
        )
        if filename:
            # Save data to the selected file
            with open(filename, "w") as f:
                f.write(str(self.inputAlphabetText.toPlainText()) + "\n")
                f.write(str(self.inputStringText.toPlainText()) + "\n")
                f.write(str(self.machineStatesText.toPlainText()) + "\n")
                f.write(str(self.jumpsDeclareText.toPlainText()) + "\n")

            print("Data saved to file:", filename)

    def loadConfigAction(self):
        # Check if default_dir exists, and create it if it doesn't
        if not os.path.exists(dialogDefaultDir):
            os.makedirs(dialogDefaultDir)

        # Open fileDialog
        filename, _ = QFileDialog.getOpenFileName(
            None,
            "Save Configuration File",
            dialogDefaultFile,
            "JFA Config Files (*.JFACON)",
            options=dialogOptions,
        )

        if filename:
            # Load data from the selected file
            with open(filename, "r") as f:
                # Update variables based on file content
                self.alphabet = f.readline().strip()
                self.inputString = f.readline().strip()
                self.machineStates = f.readline().strip()
                self.jTransitions = f.read().strip()

            print("Data loaded from file:", filename)

        # Set text fields to new variables
        self.inputAlphabetText.setText(self.alphabet)
        self.inputStringText.setText(self.inputString)
        self.machineStatesText.setText(self.machineStates)
        self.jumpsDeclareText.setText(self.jTransitions)

    def startAction(self):
        try:
            # Get and filter inputs
            self.alphabet = preRun.filterMachineAlphabet(
                self.inputAlphabetText.toPlainText()
            )
            self.inputString, self.formattedInputDict = preRun.filterInputString(
                self.inputStringText.toPlainText(), self.alphabet
            )
            self.inputStringStart = self.inputString
            self.currentReadSymbol = self.inputString[0]

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
            # Prevent empty selection
            if tmp != "No Selection":
                self.startState = tmp

            # Check evaluation characteristic radio buttons and update flag
            if self.OneWayRadioButton.isChecked():
                self.oneWay = True
            elif self.BothWaysRadioButton.isChecked():
                self.oneWay = False

            # Check determinism characteristic radio buttons and update flag
            if self.DJFARadioButton.isChecked():
                self.deterministic = True
            elif self.NJFARadioButton.isChecked():
                self.deterministic = False

            # Go through all checkboxes and check if they are selected
            # If they are, add them to list as str
            self.endStates = [checkbox.text() for checkbox in self.checkBoxList if checkbox.isChecked()]

            # Get and filter inputs
            self.machineStates, self.currentState = preRun.filterMachineStates(
                self.machineStatesText.toPlainText(), self.startState, self.endStates
            )

            self.jTransitions = preRun.filterJumpTransitions(
                self.jumpsDeclareText.toPlainText(), self.alphabet, self.machineStates
            )

            # Preemptively clear some variables
            self.readSymbols.clear()

            # If all passed, tell the user
            self.statusText.setText("Passed!\n" "Machine has been loaded!")

            # Print formatted input string to text field
            self.outputStringTextFormatted.setText(formattedInputStrToPrint)

            # Debug print
            print(
                f"\nSpecified alphabet: {self.alphabet}\nSpecified input str: {self.inputString}\nSpecified states:"
                f" {self.machineStates}\nSpecified starting state: {self.startState}\n"
                f"Specified end states: {self.endStates}\nSpecified jumps: {self.jTransitions}"
            )

            # If all passed, flip the flag for steps
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

            # Generate labels for an instance of JFA with their content
            self.labelString = QLabel("".join(self.inputString))
            self.labelState = QLabel(f"Current state: <b>{self.startState}</b>")

            self.labelJumps = QLabel(
                str(
                    runLogicDET.findNextJumps(
                        self.jTransitions, self.currentState, self.inputString
                    )
                )
            )

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
        except (
            EmptyFieldError,
            InvalidAlphabetFormatError,
            InvalidSymbolInAlphabetError,
            InputSymbolNotInAlphabetError,
            StartStateNotFoundError,
            EndStateNotFoundError,
            StateDoesNotExistError,
            SymbolDoesNotExistError,
        ) as exc:
            self.statusText.setText(f"<b>ERROR</b><br><br>{exc}")

    @staticmethod
    def exitAction():
        # Called when the exit button is pressed
        # Closes the window and terminates the process
        sys.exit(1)

    def loadStatesAction(self):
        # Pull inputted states from text box and split them into a list
        states = self.machineStatesText.toPlainText().replace("\n", "").split(";")

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
        if len(states) == 1 and states[0] == "":
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
        # Check to see if JFA was loaded
        if not self.machineStarted:
            return

        # Try/Catch for custom exceptions
        try:
            # Call the main method based on radio button selection
            if self.OneWayRadioButton.isChecked():
                (
                    self.formattedInputDict,
                    self.inputString,
                    self.currentState,
                    self.prevInfo,
                ) = runLogicDET.findAndRunJumpOneSide(
                    self.jTransitions,
                    self.currentState,
                    self.machineStates,
                    self.formattedInputDict,
                    self.inputString,
                )
            elif self.BothWaysRadioButton.isChecked():
                (
                    self.formattedInputDict,
                    self.inputString,
                    self.currentState,
                    self.prevInfo,
                ) = runLogicDET.findAndRunJumpBothSides(
                    self.jTransitions,
                    self.currentState,
                    self.machineStates,
                    self.formattedInputDict,
                    self.inputString,
                )

            # Update status text with user feedback
            self.statusText.setText(
                f"A jump has been performed!\n{self.prevInfo[0]} -> {self.currentState}"
                f" via reading {self.prevInfo[1]}"
            )

            # Debug prints
            # TODO: Remove
            print(f"\nA jump has been performed\nNew formatted string:")

            for key in self.formattedInputDict:
                print(f"Key: '{key}': {self.formattedInputDict[key]}")

        except NoJumpToPerform as exc:
            self.statusText.setText(f"<b>ERROR</b><br><br>{exc}")

        # Debug print
        # TODO: Remove
        print(
            f"\nNew input string: {self.inputString}"
            f"\nNew current state: {self.currentState}"
        )

        # Initialize/reinitialize the output string
        labelString = ""
        markedGreen = False
        symbolToUpdate = ""

        # Iterate over each symbol in the input string
        for i, symbol in enumerate(self.inputStringStart):
            # Check if the current symbol was just read by the JFA
            if symbol == self.prevInfo[1] and not markedGreen:
                # If the current symbol was just read, format it with green color,
                # then temporarily save the writen symbol and it's possition.
                labelString += f"<span style='color:green'>{symbol}</span>"
                symbolToUpdate = [symbol, i]

                # Flip the bool value to prevent multiple green symbols
                markedGreen = True

                # After that, skip this iteration
                continue

            # Check if the symbol has been read by the JFA before
            if [symbol, i] in self.readSymbols:
                # If the symbol has been read before, format it with red color
                labelString += f"<span style='color:red'>{symbol}</span>"
            else:
                # If the symbol has not been read before, format it with black color
                labelString += f"<span style='color:black'>{symbol}</span>"

        # Add the instance of written symbol and its position to a global list
        self.readSymbols.append(symbolToUpdate)
        # Update the content of instance string label
        self.labelString.setText(labelString)

        # Update the state label with new current state
        self.labelState.setText(f"Current state: <b>{self.currentState}</b>")

        # Update the jumps label with new text
        self.labelJumps.setText(
            str(
                runLogicDET.findNextJumps(
                    self.jTransitions, self.currentState, self.inputString
                )
            )
        )

        # Once the input string is empty, check if JFA is accepted or not
        if len(self.inputString) == 0:
            if self.currentState in self.endStates:
                # Debug print
                # TODO: Delete later
                print("END! ACCEPTED")
                self.statusText.setText(
                    f"<b>Machine ACCEPTED</b><br>"
                    f"A jump has been performed!<br>{self.prevInfo[0]} -> {self.currentState}"
                    f" via reading {self.prevInfo[1]}"
                )
            else:
                self.statusText.setText(
                    f"<b>Machine REFUSED</b><br>"
                    f"A jump has been performed!<br>{self.prevInfo[0]} -> {self.currentState}"
                    f" via reading {self.prevInfo[1]}"
                )

            # Flip the flag to prevent running logic on empty data
            self.machineStarted = False

    def runToEndAction(self):
        while self.machineStarted:
            self.stepAction()

    def __init__(self):
        QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)

        self.machineStarted = False
        self.oneWay = True
        self.deterministic = True
        self.startState = ""
        self.endStates = []

        self.alphabet = ""
        self.inputString = ""
        self.inputStringStart = ""
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
        self.prevInfo = ""
        self.checkBoxList = []
        self.readSymbols = []

        self.formattedInputDict = []

        self.exitButton.clicked.connect(self.exitAction)
        self.startButton.clicked.connect(self.startAction)
        self.stepButton.clicked.connect(self.stepAction)
        self.runToEndButton.clicked.connect(self.runToEndAction)

        self.SaveButton.clicked.connect(self.saveConfigAction)
        self.LoadButton.clicked.connect(self.loadConfigAction)

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
        myappid = "JFA.Sim"
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainAppWindow()
    window.show()
    sys.exit(app.exec_())
