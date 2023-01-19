from customExceptions import *


def filterMachineAlphabet(unfiltered):
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

    return unfiltered


def filterMachineStates(unfiltered):
    # Helping flags
    hasStartState = False
    hasEndState = False

    # Split string by division symbol
    unfiltered = unfiltered.split(";")

    # Check if list is not empty
    if len(unfiltered) == 1 and unfiltered[0] == '':
        raise EmptyFieldError("Machine states field")

    # Failsafe to remove last empty field if user ended string with ';'
    for entry in unfiltered:
        if len(entry) == 0:
            unfiltered.remove(entry)

    # Go through entries and check for start and end fields
    # Need at least one of each
    for entry in unfiltered:
        if not hasStartState and entry[0] == '@':
            hasStartState = True
        elif not hasEndState and entry[0] == '!':
            hasEndState = True

    # Call exceptions based on flags
    if not hasStartState:
        raise StartStateNotFoundError()
    if not hasEndState:
        raise EndStateNotFoundError()

    return unfiltered


def filterJumpTransitions(unfiltered, alphabet):

    # Remove redundant whitespaces, split by new line and split each separate line by separator characters
    filteredJumpEntriesList = []
    for entry in unfiltered.replace(" ", "").split('\n'):
        filteredJumpEntriesList.append(entry.split("-"))
