from customExceptions import NoJumpToPerform


def findAndRunJumpOneSide(jTransitions, currentState, machineStates, inputDict, inputString, lastPos):
    listOfEndpoints = []

    for entry in jTransitions:
        if entry[0] == currentState and entry[1] in inputString:
            listOfEndpoints.append(entry)

    if len(listOfEndpoints) != 1:
        raise NoJumpToPerform(currentState)

    state = listOfEndpoints[0][2]
    if state not in machineStates:
        raise RuntimeError

    currentReadSymbol = listOfEndpoints[0][1]

    if inputDict[currentReadSymbol] > 1:
        inputDict[currentReadSymbol] -= 1
    else:
        inputDict[currentReadSymbol] = 0

    outputString1 = ""
    outputString2 = ""
    symbolPosition = lastPos
    readSymbolIndex = -1
    symbolReached = False
    for symbol in inputString[lastPos:]:
        if symbol == "_":
            outputString2 += "_"
            symbolPosition += 1
            continue

        elif symbol == currentReadSymbol and not symbolReached:
            symbolReached = True
            outputString2 += "_"
            readSymbolIndex = symbolPosition
            continue

        else:
            outputString2 += symbol
            symbolPosition += 1

    symbolPosition = 0
    for symbol in inputString[:lastPos]:
        if symbol == "_":
            outputString1 += "_"
            symbolPosition += 1
            continue

        if symbol == currentReadSymbol and not symbolReached:
            symbolReached = True
            outputString1 += "_"
            readSymbolIndex = symbolPosition
            continue

        else:
            outputString1 += symbol
            symbolPosition += 1

    outputString = outputString1+outputString2
    previousInfo = [listOfEndpoints[0][0], listOfEndpoints[0][1]]
    currentState = listOfEndpoints[0][2]

    return inputDict, outputString, currentState, previousInfo, readSymbolIndex


def findAndRunJumpBothSides(jTransitions, currentState, machineStates, inputDict, inputString):
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
    symbolPosition = 0
    readSymbolIndex = -1
    symbolReached = False
    for symbol in inputString:
        if symbol == "_":
            outputString += "_"
            symbolPosition += 1

        elif symbol == currentReadSymbol and not symbolReached:
            symbolReached = True
            outputString += "_"
            readSymbolIndex = symbolPosition
            continue

        else:
            outputString += symbol
            symbolPosition += 1

    return inputDict, outputString, currentState, previousInfo, readSymbolIndex


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
