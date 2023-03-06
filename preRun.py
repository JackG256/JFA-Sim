from customExceptions import *
from main import MainAppWindow


def filterMachineAlphabet(unfiltered):
    """
    Filtering function that takes input from 'Machine Alphabet' field.
    Input is filtered into a list and ran through a few test checks for validity and consistency
    and returned as a formatted list

    :param unfiltered: string value from field
    :exception EmptyFieldError: Custom exception, raised when input field is empty, takes string name of field as input
    :exception InvalidAlphabetFormatError: Custom exception, raised when there is more than 1 symbol in any list entry
    :exception InvalidSymbolInAlphabetError: Custom exceptions, raised when any symbol in list
               is not alphabetic or numeric value

    :return unfiltered: Alphabet in form of a list of all provided symbols
    """

    # Split string by division symbol
    unfiltered = unfiltered.split(";")

    # Check if list is not empty
    if len(unfiltered) == 1 and unfiltered[0] == '':
        raise EmptyFieldError("Input alphabet field")

    # Failsafe to remove last empty field if user ended string with ';'
    for entry in unfiltered:
        if len(entry) == 0:
            unfiltered.remove(entry)

    # Check if alphabet is inputted one symbol at a time
    # Check if all symbols are valid letters
    for symbol in unfiltered:
        if len(symbol) != 1:
            raise InvalidAlphabetFormatError(symbol)

        if not symbol.isalpha() and not symbol.isnumeric():
            raise InvalidSymbolInAlphabetError(symbol)

    return unfiltered


def filterInputString(unfiltered, alphabet):
    """
    Filter function that takes input from 'Input String Field'
    Input is filtered into a list and ran through a few test checks for validity and consistency
    and returned as a formatted list

    Creates formattedDict dictionary that stores occurences of each symbol in key-value pairs.

    :param unfiltered: string value from input field
    :param alphabet: a list of all recognized letters
    :exception EmptyFieldError: Custom exception, raised when input field is empty, takes string name of field as input
    :exception InputSymbolNotInAlphabetError: Custom expection, raised when any inputted symbol is not pressed
               in machine alphabet

    :return unfiltered: Machine recognized input string in the form of a list of symbols
    """

    # Split string into char list
    unfiltered = [*unfiltered]

    # Check if list is not empty
    # Different from before, conversion not via split leaves 0 entries,
    # split() conversion leaves at least 1 empty entry
    if len(unfiltered) == 0:
        raise EmptyFieldError("Input string field")

    # Check if all symbols contained in alphabet
    for symbol in unfiltered:
        if symbol not in alphabet:
            raise InputSymbolNotInAlphabetError(symbol, alphabet)

    # Create a dictionary to store number of occurences in string
    formattedDict = {}

    # Create a dict entry for each unique symbol with the value of number of occurences
    for unique in sorted(list(dict.fromkeys(unfiltered))):
        formattedDict[unique] = unfiltered.count(unique)

    return unfiltered, formattedDict


def filterMachineStates(unfiltered, startMarked, endMarked):
    """
    Filtering function that takes input from 'Machine States field'
    Input is filtered into a list and ran through a few test checks for validity and consistency
    and returned as a formatted list

    Contains local flags;
    hasStartState: Used to check if input contains marked starting state
    hasEndState: Used to check if input contains marked end state

    :param startMarked: An instance of selected state from 'Starting state combobox', if empty, exception is called
    :param endMarked:  A list of selected checkbox instances generated from provided machine states, has to have
                       at least 1 value
    :param unfiltered: string value from input field
    :exception EmptyFieldError: Custom exception, raised when input field is empty, takes string name of field as input
    :exception StartStateNotFoundError: Custom exception, raised when machine states do not contain starting state
    :exception EndStateNotFoundError: Custom exception, raised when machine states do not contain ending state
    :return unfiltered: Machine recognized states in the form of a list of states
    """

    # Helping flags
    hasStartState = False
    hasEndState = False

    # Helping variables
    startingState = ""

    # Split string by division symbol
    unfiltered = unfiltered.split(";")

    # Check if list is not empty
    if len(unfiltered) == 1 and unfiltered[0] == '':
        raise EmptyFieldError("Machine states field")

    # Failsafe to remove all empty fields'
    for entry in unfiltered:
        if len(entry) == 0:
            unfiltered.remove(entry)

    # Go through entries and check for start and end fields
    # Need at least one of each
    for entry in unfiltered:
        if not hasStartState and entry == startMarked:
            hasStartState = True
            startingState = startMarked
        if not hasEndState and entry in endMarked:
            hasEndState = True

    # Call exceptions based on flags
    if not hasStartState:
        raise StartStateNotFoundError()
    if not hasEndState:
        raise EndStateNotFoundError()

    return unfiltered, startingState


def filterJumpTransitions(unfiltered, alphabet, machineStates):
    """
    Filtering function that takes input from 'Jump Modes field'
    Input is filtered into a list and ran through a few test checks for validity and consistency
    and returned as a formatted list containing list entries of each function

    :param unfiltered: string value from input field
    :param alphabet: a list of all recognized letters
    :param machineStates: a list of all recognized machine states
    :exception StateDoesNotExistError: Custom exception, raised when specified state in function
               is not present within machineStates list, takes string value of non-existent state as input
    :exception SymbolDoesNotExistsError: Custome exception, raised when specified symbol in function
               is not presen within alphabet list, takes string value of non-existent symbol as input
    :return:
    """

    # Remove redundant whitespaces, split by new line and split each separate line by separator characters
    filteredJumpEntriesList = []
    for entry in unfiltered.replace(" ", "").split('\n'):
        filteredJumpEntriesList.append(entry.split("-"))

    # Test checks if information in jump transition is valid
    for entry in filteredJumpEntriesList:
        if not helpFirstStateWasProvided(entry, machineStates):
            raise StateDoesNotExistError(entry[0])

        if not helpSecondStateWasProvided(entry, machineStates):
            raise StateDoesNotExistError(entry[2])

        if not helpSymbolWasProvided(entry, alphabet):
            raise SymbolDoesNotExistError(entry[1])

    return filteredJumpEntriesList


def helpFirstStateWasProvided(inputtedJumpTransition, machinestates):
    """
    Helping function to determine whether a state provided in a jump function actually exists within automata context
    Tests only first state

    :param inputtedJumpTransition: Specified jump transition, List in format of 'state - symbol - state'
    :param machinestates: List of all specified machine states
    :return: True if first state exists withing provided machine states,
             either as normal state, start state or end state.
             Otherwise false
    """

    # Get first state from function
    firstState = inputtedJumpTransition[0]

    # Find state in machine states list
    # Since some states are marked with an additional first symbol,
    # some checks add those symbols for consistency
    if firstState in machinestates:
        return True
    elif "@" + firstState in machinestates:
        return True
    elif "!" + firstState in machinestates:
        return True

    # Default branch, state was not found
    return False


def helpSecondStateWasProvided(inputtedJumpTransition, machinestates):
    """
    Helping function to determine whether a state provided in a jump function actually exists within automata context
    Tests only sencond state

    :param inputtedJumpTransition: Specified jump transition, List in format of 'state - symbol - state'
    :param machinestates: List of all specified machine states
    :return: True if second state exists withing provided machine states,
             either as normal state, start state or end state.
             Otherwise false
    """

    # Get second state from function
    secondState = inputtedJumpTransition[2]

    # Find state in machine states list
    # Since some states are marked with an additional first symbol,
    # some checks add those symbols for consistency
    if secondState in machinestates:
        return True
    elif "@" + secondState in machinestates:
        return True
    elif "!" + secondState in machinestates:
        return True

    # Default branch, state was not found
    return False


def helpSymbolWasProvided(inputtedJumpTransition, alphabet):
    """
    Helping function to determine whether a symbol provided in a jump function actually exists within automata context

    :param inputtedJumpTransition: Specified jump transition, List in format of 'state - symbol - state'
    :param alphabet: List of all recognized symbols
    :return: True if symbol exists withing provided alphabet,
             Otherwise false
    """

    # Get required symbol from function
    symbol = inputtedJumpTransition[1]

    # Find symbol in alphabet
    if symbol in alphabet:
        return True

    # Default branch, symbol was not found
    return False
