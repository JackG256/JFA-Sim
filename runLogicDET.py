from customExceptions import NoJumpToPerform


def findAndRunJumpOneSide(
    jTransitions, currentState, machineStates, inputDict, inputString
):
    listOfEndpoints = []

    for entry in jTransitions:
        if entry[0] == currentState and entry[1] in inputString:
            listOfEndpoints.append(entry)

    if len(listOfEndpoints) != 1:
        raise NoJumpToPerform(currentState)

    state = listOfEndpoints[0][2]
    if state not in machineStates:
        raise RuntimeError

    previousInfo = [listOfEndpoints[0][0], listOfEndpoints[0][1]]
    currentState = listOfEndpoints[0][2]
    currentReadSymbol = listOfEndpoints[0][1]

    if inputDict[currentReadSymbol] > 1:
        inputDict[currentReadSymbol] -= 1
    else:
        inputDict[currentReadSymbol] = 0

    outputString = ""
    symbolReached = False
    for symbol in inputString:
        if symbol == currentReadSymbol and not symbolReached:
            symbolReached = True
            pass

        outputString += symbol

    return inputDict, outputString, currentState, previousInfo


def findAndRunJumpBothSides(
    jTransitions, currentState, machineStates, inputDict, inputString
):
    listOfEndpoints = []
    usedSymbol = ""

    for entry in jTransitions:
        if entry[0] == currentState and entry[1] in inputDict:
            usedSymbol = entry[1]
            listOfEndpoints.append(entry)

    if len(listOfEndpoints) != 1:
        raise NoJumpToPerform(currentState)

    if len(usedSymbol) > 1:
        raise RuntimeError

    state = listOfEndpoints[0][2]
    if state not in machineStates:
        raise RuntimeError

    previousInfo = [listOfEndpoints[0][0], listOfEndpoints[0][1]]
    currentState = listOfEndpoints[0][2]
    currentReadSymbol = listOfEndpoints[0][1]

    if inputDict[currentReadSymbol] > 1:
        inputDict[currentReadSymbol] -= 1
    else:
        inputDict[currentReadSymbol] = 0

    outputString = ""
    symbolReached = False
    for symbol in inputString:
        if symbol == currentReadSymbol and not symbolReached:
            symbolReached = True
            continue

        outputString += symbol

    return inputDict, outputString, currentState, previousInfo


def findNextJumps(jTransitions, currentState, inputString):
    output = ""
    maxText = 5

    for entry in jTransitions:
        if entry[0] == currentState and entry[1] in inputString:
            output += f"{entry[0]} -> {entry[2]} ( {entry[1]} )\n"
            maxText -= 1
        if not maxText:
            break

    return output
