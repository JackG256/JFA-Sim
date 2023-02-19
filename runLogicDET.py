def findAndRunJumpOneSide(jTransitions, currentState, machineStates, inputDict, inputString):
    listOfEndpoints = []

    for entry in jTransitions:
        if entry[0] == currentState and entry[1] in inputString:
            listOfEndpoints.append(entry)

    if len(listOfEndpoints) != 1:
        raise RuntimeError

    state = listOfEndpoints[0][2]
    if state not in machineStates and "!" + state not in machineStates:
        raise RuntimeError

    currentState = listOfEndpoints[0][2]
    currentReadSymbol = listOfEndpoints[0][1]

    if inputDict[currentReadSymbol] > 1:
        inputDict[currentReadSymbol] -= 1
    else:
        inputDict[currentReadSymbol] = 0

    outputString = ""
    symbolReached = False
    for symbol in inputString:
        if symbolReached:
            outputString += symbol

        if symbol == currentReadSymbol:
            symbolReached = True

    return inputDict, outputString, currentState


def findAndRunJumpBothSides(jTransitions, currentState, machineStates, inputDict, inputString):
    listOfEndpoints = []
    usedSymbol = ""

    for entry in jTransitions:
        if entry[0] == currentState and entry[1] in inputDict:
            usedSymbol = entry[1]
            listOfEndpoints.append(entry)

    if len(listOfEndpoints) != 1:
        raise RuntimeError

    if len(usedSymbol) > 1:
        raise RuntimeError

    state = listOfEndpoints[0][2]
    if state not in machineStates and "!" + state not in machineStates:
        raise RuntimeError

    currentState = listOfEndpoints[0][2]
    currentReadSymbol = listOfEndpoints[0][1]

    if inputDict[currentReadSymbol] > 1:
        inputDict[currentReadSymbol] -= 1
    else:
        inputDict[currentReadSymbol] = 0

    outputString = ""
    symbolReached = False
    for symbol in inputString:
        if symbolReached:
            outputString += symbol

        if symbol == currentReadSymbol:
            symbolReached = True

    return inputDict, outputString, currentState


