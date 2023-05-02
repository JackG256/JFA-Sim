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
import runLogicNDET

qtCreatorFile = "baseUI.ui"
helpUI = "helpWindow.ui"
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)

# Get options for file dialog
dialogOptions = QFileDialog.Options()
dialogOptions |= QFileDialog.DontUseNativeDialog

# Preset a path to the configs folder in documents
dialogDefaultDir = os.path.join(os.path.expanduser("~"), "Documents")
dialogDefaultDir = os.path.join(dialogDefaultDir, "JFA Configurations")


class MainAppWindow(QMainWindow, Ui_MainWindow):
    """
    Method called for saving JFA context to a file.
    Saves important global variables to a custom .JFACON file.
    """

    def saveConfigAction(self):
        # Check if default_dir exists, and create it if it doesn't
        if not os.path.exists(dialogDefaultDir):
            os.makedirs(dialogDefaultDir)

        # Open fileDialog
        filename, _ = QFileDialog.getSaveFileName(
            None,
            "Save Configuration File",
            dialogDefaultDir,
            "JFA Config Files (*.JFACON)",
            options=dialogOptions,
        )

        # Add extension to filename if it's not already there
        if not filename.endswith(".JFACON"):
            filename += ".JFACON"

        if filename:
            # Save data to the selected file
            with open(filename, "w") as f:
                f.write(str(self.inputAlphabetText.toPlainText()) + "\n")
                f.write(str(self.inputStringText.toPlainText()) + "\n")
                f.write(str(self.machineStatesText.toPlainText()) + "\n")
                f.write(str(self.jumpsDeclareText.toPlainText()) + "\n")

            print("Data saved to file:", filename)

    """
    Method called for loading JFA context from a file.
    Loads and updates important global variables based on content
    from a custom .JFACON file
    """

    def loadConfigAction(self):
        # Check if default_dir exists, and create it if it doesn't
        if not os.path.exists(dialogDefaultDir):
            os.makedirs(dialogDefaultDir)

        # Open fileDialog
        filename, _ = QFileDialog.getOpenFileName(
            None,
            "Load Configuration File",
            dialogDefaultDir,
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

    """
    Method called when loading the context of a JFA configuration from frontend.
    Takes user inputs, runs filters and integrity checks, updates global variables.
    Checks other input fields and updates global flags.
    Generates the instance of JFA in the instances layout.
    """

    # TODO: Updates this ^ to not break non-deterministic logic
    def startAction(self):
        try:
            # Check evaluation characteristic radio buttons and update flag
            if self.OneWayRadioButton.isChecked():
                self.oneWay = True
            elif self.BothWayRadioButton.isChecked():
                self.oneWay = False

            # Check determinism characteristic radio buttons and update flag
            if self.DJFARadioButton.isChecked():
                self.deterministic = True
            elif self.NJFARadioButton.isChecked():
                self.deterministic = False

            # Preemptively clear some variables
            self.readSymbols.clear()

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

            # Get and filter inputs
            # Get Input alphabet
            self.alphabet = preRun.filterMachineAlphabet(self.inputAlphabetText.toPlainText())

            # Get Input string and formatted
            self.inputString, self.formattedInputDict = preRun.filterInputString(self.inputStringText.toPlainText(),
                                                                                 self.alphabet)
            # Save the original input string for reference
            # This prevents incorrect info when input string gets updated in runtime
            self.inputStringStart = self.inputString

            """
            Deprecated/Obsolete code
            
            # # Code to get information about shortened string, works with symbol key-value dictionary
            # # Get keys
            # keys = list(dict.fromkeys(self.inputString))
            # values = []
            # for key in keys:
            #     # Get occurence values for each key
            #     values.append(self.formattedInputDict[key])
            
            """

            # For each key in formatted input string dictionary, put key in output string, and get occurence
            # value based on index of same key.
            # NOTE: String used purely for debug prints
            formattedInputStrToPrint = ""
            for key in self.formattedInputDict:
                formattedInputStrToPrint += f"// {key} ^ {self.formattedInputDict[key]} "

            # Final string detail
            formattedInputStrToPrint += "//"

            # Get currently selected start and end states
            tmp = self.statesCombobox.currentText()
            # Prevent empty selection
            if tmp != "No Selection":
                self.startState = tmp
            else:
                raise StartStateNotFoundError()

            # Go through all checkboxes and check if they are selected
            # If they are, add them to list as str
            # NOTE: This doesn't have to be preemptivelly cleared due to
            # implicit assignment (overwrites values from previous runs)
            self.endStates = [checkbox.text() for checkbox in self.checkBoxList if checkbox.isChecked()]

            # Get and filter inputs
            # Get list of machine states and current state
            self.machineStates, self.currentState = preRun.filterMachineStates(self.machineStatesText.toPlainText(),
                                                                               self.startState, self.endStates)

            # Get list of provided transitions
            self.jTransitions = preRun.filterJumpTransitions(self.jumpsDeclareText.toPlainText(), self.alphabet,
                                                             self.machineStates, self.deterministic)

            # Update the formatted input string text field
            self.outputStringTextFormatted.setText(formattedInputStrToPrint)

            # Debug prints
            # TODO: Potentially delete later
            print(
                f"\nSpecified alphabet: {self.alphabet}\nSpecified input str: {self.inputString}\nSpecified states:"
                f" {self.machineStates}\nSpecified starting state: {self.startState}\n"
                f"Specified end states: {self.endStates}\nSpecified jumps: {self.jTransitions}")

            # Generate labels for an instance of JFA with their content
            # Label containing input string
            self.labelString = QLabel("".join(self.inputStringStart))

            # Label containing current state (starting state)
            self.labelState = QLabel(f"Current state: <b>{self.startState}</b>")

            # Label containing all possible next jumps
            self.labelJumps = QLabel(
                str(runLogicDET.findNextJumps
                    (self.jTransitions,
                     self.currentState,
                     self.inputString)
                    )
            )

            # Main if / else blocks for generating instances
            # If deterministic behaviour, generate instance
            if self.deterministic:
                # Format labels correctly
                self.labelString.setFont(QFont("Arial", 14, QFont.Bold))
                self.labelString.setAlignment(Qt.AlignCenter)
                self.labelString.setFixedSize(158, 20)

                self.labelState.setFont(QFont("Arial", 10, QFont.Bold))
                self.labelState.setAlignment(Qt.AlignCenter)
                self.labelState.setFixedSize(158, 17)

                self.labelJumps.setFont(QFont("Arial", 12, QFont.Bold))
                self.labelJumps.setAlignment(Qt.AlignCenter)
                self.labelJumps.setFixedSize(158, 134)

                # Create a sub-layout object containing labels
                layout = QVBoxLayout()
                # Put all labels into the sub-layout
                layout.addWidget(self.labelString)
                layout.addWidget(self.labelState)
                layout.addWidget(self.labelJumpsText)
                layout.addWidget(self.labelJumps)

                # Assign the sub-layout to a layout widget
                layoutWidget = QWidget()
                layoutWidget.setFixedSize(158, 201)
                layoutWidget.setLayout(layout)

                # Add the widget to a list of widgets
                # Used to reset instances in layout if new machine loaded
                self.instancesGrid.addWidget(layoutWidget)

            # Else path if non-deterministic behaviour
            else:
                # Get the earliest possible path for one instance of non-deterministic automaton
                path = runLogicNDET.generateAdjacencyMatrix(self.jTransitions, len(self.inputStringStart),
                                                            self.inputStringStart, self.startState, self.endStates)
                # Check if method didn't return empty string (no path found)
                if path != "":
                    print(f"\n{path[0]}\n\n{path[1]}")
                else:
                    print("WRONG")

            # If all fetches and checks passed, inform the user and flig global flag
            self.statusText.setText("Passed!\n" "Machine has been loaded!")

            self.machineStarted = True

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
                InvalidDeterministicFormat
        ) as exc:
            self.statusText.setText(f"<b>ERROR</b><br><br>{exc}")

    """
    Called when the exit button is pressed.
    Closes the window and terminates the process.
    """
    @staticmethod
    def exitAction():
        sys.exit(1)

    """
    Method called for loading and generating checkbox instances.
    Called everytime the "Machine States" textbox is updated
    Generated based on user input in the 'Machine States' field.
    """
    def loadStatesAction(self):
        # Pull inputed states from text box and split them into a list via a splitting symbol
        states = self.machineStatesText.toPlainText().replace("\n", "").split(";")

        # Clear the selection combobox before assigning new values
        self.statesCombobox.clear()

        # Clear the list of checkboxes
        # NOTE: list is used to check selected checkboxes when loading automaton
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
        # NOTE: This seems to be redundant, but I am too afraid
        # to delete it in fear it might break everything
        if len(states) == 1 and states[0] == "":
            return False

        # Helping sizing variables for generating checkboxes
        num_cols = 4
        row = 0
        col = 0

        # For each state in list
        for i, state in enumerate(states):
            # Failsafe for empty entry
            if str(state) == "":
                continue

            # Add item to combobox
            self.statesCombobox.addItem(state)

            # Create a checkbox widget and assign it to the layout of checkboxes
            checkbox = QCheckBox(state)
            self.endStatesGrid.addWidget(checkbox, row, col)

            # Add instance of checkbox to global list
            self.checkBoxList.append(checkbox)

            # Update sizing variables
            col += 1
            if col == num_cols:
                col = 0
                row += 1

    """
    Method called for simulating a logical step/jump in the JFA
    Calls specific method based on user selection and updates specific variable
    to provide user feedback
    """

    def stepAction(self):
        # Check to see if JFA was loaded
        if not self.machineStarted:
            return

        # Try/Catch for custom exceptions
        try:
            # Call the main method based on radio button selection
            if self.oneWay:
                (
                    self.formattedInputDict,
                    self.inputString,
                    self.currentState,
                    self.prevInfo,
                    self.lastPos
                ) = runLogicDET.findAndRunJumpOneSide(
                    self.jTransitions,
                    self.currentState,
                    self.machineStates,
                    self.formattedInputDict,
                    self.inputString,
                    self.lastPos
                )
            else:
                (
                    self.formattedInputDict,
                    self.inputString,
                    self.currentState,
                    self.prevInfo,
                    self.lastPos
                ) = runLogicDET.findAndRunJumpBothSides(
                    self.jTransitions,
                    self.currentState,
                    self.machineStates,
                    self.formattedInputDict,
                    self.inputString,
                )

            # Update the list of read symbols (positions)
            self.readSymbols.append([self.prevInfo[1], self.lastPos])

            # Update status text with user feedback
            self.statusText.setText(
                f"A jump has been performed!\n{self.prevInfo[0]} -> {self.currentState}"
                f" via reading {self.prevInfo[1]}")

        except NoJumpToPerform as exc:
            self.statusText.setText(f"<b>ERROR</b><br><br>{exc}")

        # Debug prints
        # TODO: Remove if unnecesary

        # Print info about jump and automata
        print(f"\nA jump has been performed\nNew formatted string:")

        # Print info about new formatted string
        for key in self.formattedInputDict:
            print(f"Key: '{key}': {self.formattedInputDict[key]}")

        # Print info about new input string and current state
        print(
            f"\nNew input string: {self.inputString}"
            f"\nNew current state: {self.currentState}")

        # Initialize/reinitialize the output string to put in label
        labelString = ""

        # Helping flag to prevent multiple green symbols
        markedGreen = False
        # symbolToUpdate = ""

        # Iterate over each symbol in the input string
        for i, symbol in enumerate(self.inputStringStart):
            # Check if the current symbol was just read by the JFA
            if [symbol, i] in self.readSymbols and i == self.lastPos and not markedGreen:
                # If the current symbol was just read, format it with green color,
                # then temporarily save the writen symbol and it's possition. (now obsolete)
                labelString += f"<span style='color:green'>{symbol}</span>"
                # symbolToUpdate = [symbol, i]

                # Flip the bool value to prevent multiple green symbols
                markedGreen = True

                # After that, skip this iteration
                continue

            # Check if the symbol has been read before by the JFA before
            if [symbol, i] in self.readSymbols:
                # If the symbol has been read before, format it with red color
                labelString += f"<span style='color:red'>{symbol}</span>"
            else:
                # If the symbol has not been read before, format it with black color
                labelString += f"<span style='color:black'>{symbol}</span>"

        # Update the content of instance string label
        self.labelString.setText(labelString)

        # Update the state label with new current state
        self.labelState.setText(f"Current state: <b>{self.currentState}</b>")

        # Update the jumps label with new text
        self.labelJumps.setText(
            str(
                runLogicDET.findNextJumps(
                    self.jTransitions,
                    self.currentState,
                    self.inputString
                )
            )
        )

        # Check if every symbol in input string was read
        stringHasSymbols = False
        for symbol in self.inputString:
            if symbol != "_":
                stringHasSymbols = True

        # Once the input string is empty, check if JFA is accepted or not,
        # then print information to status textbox
        if not stringHasSymbols:
            if self.currentState in self.endStates:
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

    """
    Method to loop steps until the machine is finished evaluating
    """
    def runToEndAction(self):
        while self.machineStarted:
            self.stepAction()

    """
    MainApp class constructor.
    Sets all global variables and also edits process information.
    """
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
        self.lastPos = 0

        self.labelString = ""
        self.labelState = ""
        self.labelJumpsText = QLabel("Possible jumps\nfrom state:\n")
        self.labelJumps = ""

        self.labelJumpsText.setFont(QFont("Arial", 10, QFont.Bold))
        self.labelJumpsText.setAlignment(Qt.AlignCenter)
        self.labelJumpsText.setFixedSize(158, 30)

        self.currentReadSymbol = ""
        self.currentReadSymbolPos = 0
        self.currentState = ""
        self.prevInfo = []
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

        # Default value in selection box on run
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
