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
import runLogicBoth

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

    def saveConfigAction(self):

        """
        Method called for saving JFA context to a file.
        Saves important global variables to a custom .JFACON file.
        """

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

        # Check of only extension to prevent saving in current directury
        if filename != ".JFACON":
            # Save data to the selected file
            with open(filename, "w") as f:
                f.write(str(self.inputAlphabetText.toPlainText()) + "\n")
                f.write(str(self.inputStringText.toPlainText()) + "\n")
                f.write(str(self.machineStatesText.toPlainText()) + "\n")
                f.write(str(self.jumpsDeclareText.toPlainText()) + "\n")

                print("Data saved to file:", filename)

    def loadConfigAction(self):

        """
        Method called for loading JFA context from a file.
        Loads and updates important global variables based on content
        from a custom .JFACON file
        """

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

    def startAction(self):

        """
        Method called when loading the context of a JFA configuration from frontend.
        Takes user inputs, runs filters and integrity checks, updates global variables.
        Checks other input fields and updates global flags.
        Generates the instance of JFA in the instances' layout.
        """

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
            self.machineStarted = False

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
            self.inputStringFull = self.inputString

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



            # Get currently selected start and end states
            tmp = self.statesCombobox.currentText()
            # Prevent empty selection
            if tmp != "No Selection":
                self.startState = tmp
            else:
                raise StartStateNotFoundError()

            # Go through all checkboxes and check if they are selected
            # If they are, add them to list as str
            # NOTE: This doesn't have to be preemptively cleared due to
            # implicit assignment (overwrites values from previous runs)
            self.endStates = [checkbox.text() for checkbox in self.checkBoxList if checkbox.isChecked()]

            # Get and filter inputs
            # Get list of machine states and current state
            self.machineStates, self.currentState = preRun.filterMachineStates(self.machineStatesText.toPlainText(),
                                                                               self.startState, self.endStates)

            # Get list of provided transitions
            self.jTransitions = preRun.filterJumpTransitions(self.jumpsDeclareText.toPlainText(), self.alphabet,
                                                             self.machineStates, self.deterministic)

            # Get formmated dictionary of occurences
            formattedInputStrToPrint = runLogicBoth.generateFormattedInputDictionary(self.formattedInputDict)

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
            self.labelString = QLabel("".join(self.inputStringFull))

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

            # Main block for generating instances
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

            # If non-deterministic behaviour, try and find an accepting path
            if not self.deterministic:
                # Get the earliest possible path for one instance of non-deterministic automaton
                path = runLogicNDET.generateAdjMatrixAndPath(self.jTransitions, len(self.inputStringFull),
                                                             self.inputStringFull, self.startState, self.endStates)

                # Reset global counter for non-deterministic runtime
                self.nonDethIter = 0

                # Check if method didn't return empty string (no path found)
                if path != "":
                    # If path was found, save values and flip global flags
                    self.nonDetPathFound = True
                    self.nonDetPath = path[0]
                    self.nonDetSymbols = path[1]
                    print(f"Found acceptable path in non-deterministic evaluation:"
                          f"\n{self.nonDetPath}\n\n{self.nonDetSymbols}")

                else:
                    # If path was not found, raise exception to generate user feedback
                    self.nonDetPathFound = False
                    print("Didn't manage to find an acceptable path in non-deterministic evaluation."
                          " Throwing exception")
                    raise NoAcceptPathFound()

            # If all fetches and checks passed, inform the user and flig global flag
            self.statusText.setText("Passed!\n" "Machine has been loaded!")

            # Global flag that loading the machine was succesful
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
                InvalidDeterministicFormat,
                NoAcceptPathFound
        ) as exc:
            self.statusText.setText(f"<b>ERROR</b><br><br>{exc}")

    @staticmethod
    def exitAction():

        """
        Called when the exit button is pressed.
        Closes the window and terminates the process.
        """

        sys.exit(1)

    def loadStatesAction(self):

        """
        Method called for loading and generating checkbox instances.
        Called everytime the "Machine States" textbox is updated
        Generated based on user input in the 'Machine States' field.
        """

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

    def updateRadioButtons(self):

        """
        Method called to enable / disable correct radio buttons based on evaluation selection
        Selecting One-Way disables NJFA
        Selecting Two-ways reenables it
        """

        if self.OneWayRadioButton.isChecked():
            self.NJFARadioButton.setEnabled(False)

            self.NJFARadioButton.setChecked(False)
            self.DJFARadioButton.setChecked(True)

        elif self.BothWayRadioButton.isChecked():
            self.NJFARadioButton.setEnabled(True)

    def stepAction(self):

        """
        Method called for simulating a logical step/jump in the JFA
        Calls specific method based on user selection and updates specific variable
        to provide user feedback
        """

        # Check to see if JFA was loaded
        if not self.machineStarted:
            return

        # Try/Catch for custom exceptions
        try:
            # Call the main method based on radio button selection
            # Deterministic approach
            if self.deterministic:
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
                # Two-ways logic
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

            # Non-deterministic approach
            else:
                # Increment global index counter
                self.nonDethIter += 1

                # Get index values for previous and current information
                previousIndex = self.nonDethIter - 1
                currentIndex = self.nonDethIter

                # Manually fill the previous info variable
                # NOTE: This was normally done in a method, since we don't need to
                # search for a step to be done, we can just add it manually
                self.prevInfo = [self.nonDetPath[previousIndex], self.nonDetSymbols[previousIndex]]

                # Call a function to get index of currently read symbol in input string
                # NOTE: This was also normally done in a method, but we cannot call it here because it modifies
                # the input string in deterministic way
                (
                    self.inputString,
                    self.lastPos,
                    self.formattedInputDict
                ) = runLogicNDET.findNextSymbolPosition(
                    self.nonDetSymbols[previousIndex],
                    self.inputString,
                    self.formattedInputDict
                )

                # update current state variable
                self.currentState = self.nonDetPath[currentIndex]

            # Update the list of read symbols (positions)
            self.readSymbols.append([self.prevInfo[1], self.lastPos])

            # Update status text with user feedback
            self.statusText.setText(
                f"A jump has been performed!\n{self.prevInfo[0]} -> {self.currentState}"
                f" via reading {self.prevInfo[1]}")

        # Custom exception handling
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
        for i, symbol in enumerate(self.inputStringFull):
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
                break

        # Once the input string is empty, check if JFA is accepted or not,
        # then print information to status textbox
        if not stringHasSymbols:
            if self.currentState in self.endStates:
                self.statusText.setText(
                    f"<b>String ACCEPTED</b><br>"
                    f"A jump has been performed!<br>{self.prevInfo[0]} -> {self.currentState}"
                    f" via reading {self.prevInfo[1]}"
                )
            else:
                self.statusText.setText(
                    f"<b>String REFUSED</b><br>"
                    f"A jump has been performed!<br>{self.prevInfo[0]} -> {self.currentState}"
                    f" via reading {self.prevInfo[1]}"
                )

            # Flip the flag to prevent running logic on empty data
            self.machineStarted = False

    def runToEndAction(self):

        """
        Method to loop steps until the machine is finished evaluating
        """

        while self.machineStarted:
            self.stepAction()

    def __init__(self):

        """
        MainApp class constructor.
        Sets all global variables and also edits process information.
        """

        # Generators for application class
        QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)

        # Global flags and variables to run correct code
        self.machineStarted = False
        self.oneWay = True
        self.deterministic = True

        # Global flags and variables purely for non-deterministic runtime
        self.nonDetPathFound = False
        self.nonDetPath = []
        self.nonDetSymbols = []
        self.nonDethIter = -1

        # Global variables regarding automaton
        self.startState = ""
        self.endStates = []
        self.alphabet = ""
        self.inputString = ""
        self.inputStringFull = ""
        self.machineStates = ""
        self.jTransitions = ""
        self.lastPos = 0
        self.currentReadSymbol = ""
        self.currentReadSymbolPos = 0
        self.currentState = ""
        self.prevInfo = []
        self.formattedInputDict = []

        # Global list to keep track of other values
        # List of read symbols to prevent multiple green symbols at one step
        self.readSymbols = []
        # List of end state checkboxes, used for correct deletion and generation
        self.checkBoxList = []

        # Global variables for labels for instance layout
        self.labelString = ""
        self.labelState = ""
        self.labelJumpsText = QLabel("Possible jumps\nfrom state:\n")
        self.labelJumps = ""

        # Manual formatting of a label
        self.labelJumpsText.setFont(QFont("Arial", 10, QFont.Bold))
        self.labelJumpsText.setAlignment(Qt.AlignCenter)
        self.labelJumpsText.setFixedSize(158, 30)

        # Connect control action to corresponding control buttons
        self.exitButton.clicked.connect(self.exitAction)
        self.startButton.clicked.connect(self.startAction)
        self.stepButton.clicked.connect(self.stepAction)
        self.runToEndButton.clicked.connect(self.runToEndAction)

        # Connect file management action to corresponding file buttons
        self.SaveButton.clicked.connect(self.saveConfigAction)
        self.LoadButton.clicked.connect(self.loadConfigAction)

        # Connect radio buttons update action to corresponding radio buttons
        self.BothWayRadioButton.clicked.connect(self.updateRadioButtons)
        self.OneWayRadioButton.clicked.connect(self.updateRadioButtons)

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
