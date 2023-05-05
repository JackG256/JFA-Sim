import unittest
import preRun
from customExceptions import *


class test_Case_FilterAlphabet(unittest.TestCase):
    def test_filterAlphabetPass(self):
        inputData = "A;B;C;D;E;F"
        outputData = preRun.filterMachineAlphabet(inputData)

        expectedData = ['A', 'B', 'C', 'D', 'E', 'F']
        self.assertEqual(outputData, expectedData)

    def test_filterAlphabetException(self):
        inputData = "A;B;C;DD;E;F"
        with self.assertRaises(InvalidAlphabetFormatError):
            preRun.filterMachineAlphabet(inputData)

    def test_filterAlphabetEmpty(self):
        inputData = ""
        with self.assertRaises(EmptyFieldError):
            preRun.filterMachineAlphabet(inputData)


class test_Case_FilterInputString(unittest.TestCase):
    def test_filterInputStringPass(self):
        inputAlphabet = ["A", "B", "C", "D"]
        inputData = "ABBDCA"
        outputString, outputDict = preRun.filterInputString(inputData, inputAlphabet)

        expectedString = ['A', 'B', 'B', 'D', 'C', 'A']
        expectedDict = {
            "A": 2,
            "B": 2,
            "C": 1,
            "D": 1
        }

        self.assertEqual(outputString, expectedString)
        self.assertEqual(outputDict, expectedDict)

    def test_filterInputStringEmpty(self):
        inputData = ""
        inputAlphabet = ""
        with self.assertRaises(EmptyFieldError):
            preRun.filterInputString(inputData, inputAlphabet)

    def test_filterInputStringIncorrectAlphabet(self):
        inputData = "ABC"
        inputAlphabet = []
        with self.assertRaises(InputSymbolNotInAlphabetError):
            preRun.filterInputString(inputData, inputAlphabet)

        inputAlphabet = ["A", "B"]

        with self.assertRaises(InputSymbolNotInAlphabetError):
            preRun.filterInputString(inputData, inputAlphabet)


class test_Case_FilterMachineStates(unittest.TestCase):
    def test_filterMachineStatesPass(self):
        inputData = "Q0;Q1;Q2;Q3"

        outputData = preRun.filterMachineStates(inputData)

        expectedData = ["Q0", "Q1", "Q2", "Q3"]
        self.assertEqual(expectedData, outputData)

    def test_filterMachineStatesEmpty(self):
        inputData = ""
        with self.assertRaises(EmptyFieldError):
            preRun.filterMachineStates(inputData)


class test_Case_FilterJumpTransitions(unittest.TestCase):
    def test_filterJumpTransitionsPass(self):
        inputData = (f"Q0 - A - Q1\n"
                     f"Q1-B- Q2\n"
                     f"Q2-C-Q3\n")

        inputAlphabet = ["A", "B", "C"]
        inputStates = ["Q0", "Q1", "Q2", "Q3"]
        inputDeterministic = True

        outputData = preRun.filterJumpTransitions(inputData, inputAlphabet, inputStates, inputDeterministic)

        expectedData = [['Q0', 'A', 'Q1'], ['Q1', 'B', 'Q2'], ['Q2', 'C', 'Q3']]

        self.assertEqual(expectedData, outputData)

    def test_filterJumpTransitionsStateNotExistent(self):
        inputData = (f"Q0 - A - Q1\n"
                     f"Q1-B- Q2\n"
                     f"Q2-C-Q3\n")

        inputAlphabet = ["A", "B", "C"]
        inputStates = ["Q0", "Q1", "Q2"]
        inputDeterministic = True

        with self.assertRaises(StateDoesNotExistError):
            preRun.filterJumpTransitions(inputData, inputAlphabet, inputStates, inputDeterministic)

    def test_filterJumpTransitionsSymbolNotExistent(self):
        inputData = (f"Q0 - A - Q1\n"
                     f"Q1-B- Q2\n"
                     f"Q2-C-Q3\n")

        inputAlphabet = ["A", "B"]
        inputStates = ["Q0", "Q1", "Q2", "Q3"]
        inputDeterministic = True

        with self.assertRaises(SymbolDoesNotExistError):
            preRun.filterJumpTransitions(inputData, inputAlphabet, inputStates, inputDeterministic)

    def test_filterJumpTransitionsNotDeterministic(self):
        inputData = (f"Q0 - A - Q1\n"
                     f"Q1-B- Q2\n"
                     f"Q1-B-Q3\n")

        inputAlphabet = ["A", "B", "C"]
        inputStates = ["Q0", "Q1", "Q2", "Q3"]
        inputDeterministic = True

        with self.assertRaises(InvalidDeterministicFormatError):
            preRun.filterJumpTransitions(inputData, inputAlphabet, inputStates, inputDeterministic)


if __name__ == '__main__':
    unittest.main()
