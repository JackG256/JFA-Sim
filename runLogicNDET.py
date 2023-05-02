import numpy as np


def generateAdjacencyMatrix(jTransitions, iterationMax, inputString, startState, endStates):
    initialMatrix, loadedStates = createInitialMatrix(jTransitions)

    nextMatrix = np.array(initialMatrix)
    matrixConstant = nextMatrix

    for _ in range(1, iterationMax):
        nextMatrix = np.dot(nextMatrix, matrixConstant)

    startStateCoord = loadedStates.index(startState)
    endStatesCoords = [loadedStates.index(endstate) for endstate in endStates]
    path = ""
    for xCoord in endStatesCoords:
        if nextMatrix[startStateCoord, xCoord] == 1:
            path = findPath(jTransitions, startState, loadedStates[xCoord], iterationMax)

            if path is not None:
                readSymbols = ''.join(sorted(path[1]))
                sortedString = ''.join(sorted(inputString))
                if readSymbols == sortedString:
                    break

                path = ""
                # TODO: Add checks for one-way / two way automata. Right now they are not checked

    return path


def createInitialMatrix(statePaths):
    # Helping variable to store list of active states
    loadedStates = []

    # Find all active states based on Jump Transitions
    for entry in statePaths:
        if entry[0] not in loadedStates:
            loadedStates.append(entry[0])
        if entry[2] not in loadedStates:
            loadedStates.append(entry[2])

    # Sort list alphabetically for easier evaluation
    loadedStates = sorted(loadedStates)

    # Get number of items in list
    xySize = len(loadedStates)

    # Create a 2D matrix with zeroes to store data into
    initialMatrix = [[0 for _ in range(xySize)] for _ in range(xySize)]
    # Create a 2D matrix with empty string spaces to store symbol data into
    pathMatrix = [["" for _ in range(xySize)] for _ in range(xySize)]

    # Iterate through active states and fill adjacency matrix if paths exist
    for i, stateY in enumerate(loadedStates):
        for j, stateX in enumerate(loadedStates):
            # Compare every pair of states with transition entries
            for entry in statePaths:
                # If checks, write a value to adjacency matrix and save transition for later use
                if stateY == entry[0] and stateX == entry[2]:
                    initialMatrix[i][j] += 1

    return initialMatrix, loadedStates


"""
Old version of evaluating NJFA via matrix math
Too complicated, was scrapped
"""
# def stepAdjacencyMatrix(initialMatrix, matrixConstant, pathMatrix, jTransitions, loadedStates):
#     nextMatrix = initialMatrix @ matrixConstant
#     nextPathMatrix = np.zeros_like(pathMatrix, dtype='U10')
#     nextPathMatrix.fill("")
#
#     initState = ""
#     betweenState = ""
#     symbolToAdd = ''
#     newString = ""
#     listOfPaths = []
#     foundInfo = False
#
#     # For each row
#     for j, yValue in enumerate(nextMatrix):
#
#         # For each column
#         for i, xValue in enumerate(yValue):
#
#             # If this cell is 1, find what target state it represents
#             if xValue == 1:
#                 stateTo = loadedStates[i]
#
#                 # For this state, find any transitions where this is a target state
#                 for entry in jTransitions:
#                     if entry[2] == stateTo:
#
#                         # Save from what state it transitioned for later
#                         # Save symbol to update for later
#                         betweenState = entry[0]
#                         symbolToAdd = entry[1]
#
#                         # Based on state on start of transition, find state 1 transition before this one
#                         # and save the initial state
#                         for previousEntry in jTransitions:
#                             if previousEntry[2] == betweenState and loadedStates[j] == previousEntry[0]:
#                                 initState = previousEntry[0]
#                                 foundInfo = True
#                                 break
#
#                         if foundInfo:
#                             # Save indexes to search in matrix
#                             yCoord = loadedStates.index(initState)
#                             xCoord = loadedStates.index(betweenState)
#
#                             # Get content of previous path matrix on correct coordinates
#                             # (initial state ; inbetween state)
#                             stringToPrepend = pathMatrix[yCoord, xCoord]
#                             # Split the string into list over hashtags for easier  manipulation
#                             listOfSymbols = stringToPrepend.split("#")
#
#                             # For each string value from previous list add new symbol and splitting symbol
#                             for oldString in listOfSymbols:
#                                 newString += oldString + symbolToAdd + "#"
#
#                             # Remove last unnecesary spliting symbol
#
#                             # Update coordinates for newer matrix
#                             yCoord = loadedStates.index(initState)
#                             xCoord = loadedStates.index(stateTo)
#
#                             # Save the updated value to new path matrix
#                             nextPathMatrix[yCoord, xCoord] = newString
#
#                             # Clear the string for future inserts
#                             newString = ""
#
#                         foundInfo = False
#
#     nextPathMatrix = nextPathMatrix.tolist()
#
#     for i, row in enumerate(nextPathMatrix):
#         for j, cell in enumerate(row):
#             if cell != "" and cell[-1] == "#":
#                 nextPathMatrix[i][j] = cell[:-1]
#
#     nextPathMatrix = np.array(nextPathMatrix)
#
#     # return values
#     return nextMatrix, nextPathMatrix


def findPath(transitions, startState, endState, moves, path=None, symbols=None):
    """
    :param transitions: an oriented graph represented as a list of values
                        in the format of [[stateX], [symbol], [stateY]]
    :param startState: the starting state
    :param endState: the ending state
    :param moves: the number of moves allowed
    :param path: a list to store the states in the path
    :param symbols: a list to store the symbols on the edges of the path
    :return: a list containing a list of states representing a path from startState to endState
            in the graph in n moves and a list of symbols on the "edges" of the path (symbols read),
            or None if no such path exists
    """

    # Initialize the path and symbols lists if they are not provided
    if path is None:
        path = [startState]
    if symbols is None:
        symbols = []

    # If no moves left, check if we have arrived at the end state
    if moves == 0:
        if startState == endState:
            # If the end state has been reached, return the path and symbols
            return [path, symbols]
        else:
            # If the end state has not been reached, return None
            return None

    # If there is only one move left
    elif moves == 1:
        for stateX, symbol, stateY in transitions:
            if stateX == startState and stateY == endState:
                # If the edge connects the start and end states, return the path and symbols
                # with the new state and symbol added
                return [path + [endState], symbols + [symbol]]
        # If no edge connects the start and end states, return None
        return None

    # If there are more than one moves left
    else:
        for stateX, symbol, stateY in transitions:
            if stateX == startState:
                new_path = path + [stateY]
                new_symbols = symbols + [symbol]
                # Recursively call findPath on the neighbor of the start state with moves decremented by 1
                result = findPath(transitions, stateY, endState, moves - 1, new_path, new_symbols)
                if result is not None:
                    # If a path is found, return it
                    return result
        # If no path is found, return None
        return None
