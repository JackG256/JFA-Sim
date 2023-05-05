from customExceptions import NoJumpToPerform


def findAndRunJumpOneSide(jTransitions, currentState, inputDict, inputString, lastPos):
    """
    Given a list of jump transitions, the current state, input dictionary, input string, and last position,
    searches for the next jump endpoint on the current side of the input string and returns the updated input
    dictionary, output string, current state, previous info tuple, and the index of the read symbol.

    :param jTransitions: A list of jump transitions in the format [[stateX], [symbol], [stateY]]
    :param currentState: The current state in the machine
    :param inputDict: A dictionary that stores the count of remaining symbols to be read from the input string
    :param inputString: The input string to the machine
    :param lastPos: The last position of the machine on the input string
    :raises NoJumpToPerform: Custom exception, raised when no suitable transition was found
    :return: A tuple containing the updated input dictionary, the output string, the current state,
             the previous info tuple [stateX, symbol], and the index of the read symbol
    """

    # Variable declaration
    listOfEndpoints = []

    # Go through all transitions
    # Save all relative to intial and target state
    for entry in jTransitions:
        if entry[0] == currentState and entry[1] in inputString:
            listOfEndpoints.append(entry)

    # If there are no transitions, throw custom error
    # NOTE: length of listOfEndpoints should never go above 1, prevented by sanity checks
    if len(listOfEndpoints) != 1:
        raise NoJumpToPerform(currentState)

    # Get currently read symbol from transition
    currentReadSymbol = listOfEndpoints[0][1]

    # Update formatted input dictionary
    if inputDict[currentReadSymbol] > 1:
        inputDict[currentReadSymbol] -= 1
    else:
        inputDict[currentReadSymbol] = 0

    # Start searching throgh input string for symbol
    outputString1 = ""
    outputString2 = ""
    symbolPosition = lastPos
    readSymbolIndex = -1
    symbolReached = False

    # First loop, searches from last read symbol to end
    for symbol in inputString[lastPos:]:
        # if empty, write and continue
        if symbol == "_":
            outputString2 += "_"
            symbolPosition += 1

        # if first found, save index, flip flag, write empty and continue
        elif symbol == currentReadSymbol and not symbolReached:
            symbolReached = True
            outputString2 += "_"
            readSymbolIndex = symbolPosition

        # otherwise write and continue
        else:
            outputString2 += symbol
            symbolPosition += 1

    # Second loop, searches from first to last read symbol - 1
    symbolPosition = 0
    for symbol in inputString[:lastPos]:
        # if empty, write and continue
        if symbol == "_":
            outputString1 += "_"
            symbolPosition += 1
            continue

        # if first found, save index, flip flag, write empty and continue
        if symbol == currentReadSymbol and not symbolReached:
            symbolReached = True
            outputString1 += "_"
            readSymbolIndex = symbolPosition
            continue

        # otherwise write and continue
        else:
            outputString1 += symbol
            symbolPosition += 1

    # Join strings together
    # Save information to a tuple and return
    outputString = outputString1+outputString2
    previousInfo = [listOfEndpoints[0][0], listOfEndpoints[0][1]]
    currentState = listOfEndpoints[0][2]

    return inputDict, outputString, currentState, previousInfo, readSymbolIndex


def findAndRunJumpBothSides(jTransitions, currentState, inputDict, inputString):
    """
    Find a transition from the given current state using the given jumps (jTransitions).
    Modify the input dictionary (inputDict) to reflect the current read symbol and the current state.
    Generate the output string (outputString) and return the required data.

    :param jTransitions: list of possible transitions (current state, read symbol, target state)
    :param currentState: current state from which to start the transition
    :param inputDict: dictionary of symbols with their respective frequencies
    :param inputString: input string on which to perform transitions
    :return: tuple containing inputDict, outputString, currentState, previousInfo, and readSymbolIndex
    :raises NoJumpToPerform: if there are no transitions or more than one transition from the current state
    :raises RuntimeError: if the target state is not defined in the machine states
    """
    # Variable declaration
    listOfEndpoints = []

    # Go through all transitions
    # Save all relative to intial and target state
    for entry in jTransitions:
        if entry[0] == currentState and entry[1] in inputDict:
            listOfEndpoints.append(entry)

    # If there are no transitions, throw custom error
    # NOTE: length of listOfEndpoints should never go above 1, prevented by sanity checks
    if len(listOfEndpoints) != 1:
        raise NoJumpToPerform(currentState)

    # Save information to a tuple
    previousInfo = [listOfEndpoints[0][0], listOfEndpoints[0][1]]
    currentState = listOfEndpoints[0][2]
    # Get currently read symbol
    currentReadSymbol = listOfEndpoints[0][1]

    # Update formatted input dictionary
    if inputDict[currentReadSymbol] > 1:
        inputDict[currentReadSymbol] -= 1
    else:
        inputDict[currentReadSymbol] = 0

    # Start searching throught input string for symbol
    # Looks always left to right
    outputString = ""
    symbolPosition = 0
    readSymbolIndex = -1
    symbolReached = False
    # Go through all symbols in input string
    for symbol in inputString:
        # if empty, write and continue
        if symbol == "_":
            outputString += "_"
            symbolPosition += 1

        # if first found, save index, flip flag, write empty and continue
        elif symbol == currentReadSymbol and not symbolReached:
            symbolReached = True
            outputString += "_"
            readSymbolIndex = symbolPosition

        # otherwise write and continue
        else:
            outputString += symbol
            symbolPosition += 1

    return inputDict, outputString, currentState, previousInfo, readSymbolIndex

