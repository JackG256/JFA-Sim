def findAndRunJumpOneSide(jTransitions, currentReadSymbol, currentState, machineStates, inputString):
    listOfEndpoints = []
    for entry in jTransitions:
        if entry[0] == currentState and entry[1] in inputString:
            listOfEndpoints.append(entry)

    if len(listOfEndpoints) != 1:
        pass
        # TODO: implement exception

    if listOfEndpoints[0][2] not in machineStates:
        pass
        # TODO: implement exception

    currentState = listOfEndpoints[0][2]
    currentReadSymbol = listOfEndpoints[0][1]

    outputString = ""
    symbolReached = False
    for symbol in inputString:
        if symbolReached:
            outputString += symbol

        if symbol == currentReadSymbol:
            symbolReached = True



    # Format: Status,
    return outputString, currentState