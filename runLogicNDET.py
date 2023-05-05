import numpy as np
import time


def generateAdjMatrixAndPath(jTransitions, iterationMax, inputString, startState, endStates):
    """
    Generate the adjacency matrix for a Jumping Finite Automaton (JFA) and find a path
    from the start state to one of the end states that matches a given input string.

    :param jTransitions: A list containing the transitions of the automata
    :param iterationMax: The maximum number of iterations to perform when generating the adjacency matrix
    :param inputString: The input string to match
    :param startState: The starting state for the path
    :param endStates: A list of end states to search for a path to
    :return The path from the start state to one of the end states
    that matches the input string, or an empty string if no such path exists
    """

    # Create an adjacency matrix of first rank and sorted list of active states (used as coordinates)
    initialMatrix, loadedStates = createInitialMatrix(jTransitions)

    # Transform nested list into numpy matrix for easier calculation
    nextMatrix = np.array(initialMatrix)

    # Raise adjacency matrix to the power of
    # number of symbols in input string
    nextMatrix = np.linalg.matrix_power(nextMatrix, iterationMax)

    # Get coordinate of initial state
    startStateCoord = loadedStates.index(startState)
    # Get coordinates of end states
    endStatesCoords = [loadedStates.index(endstate) for endstate in endStates]

    returnPath = None
    validPathFound = False
    # Iterativelly check over all coordinates if value of cell is greater than 1
    # (a path in n moves exist from start state to end state exists)
    for xCoord in endStatesCoords:
        if validPathFound:
            break

        if nextMatrix[startStateCoord, xCoord] >= 1:
            # Try to find first accepting path
            path = findPath(jTransitions, startState, loadedStates[xCoord], iterationMax)

            # if path exists, check if symbols read along the way match up symbols in input string
            if path is not None:
                for i, entry in enumerate(path):

                    readSymbols = ''.join(sorted(entry[1]))
                    sortedString = ''.join(sorted(inputString))
                    # If yes, break and return
                    if readSymbols == sortedString:
                        returnPath = [entry[0], entry[1]]
                        validPathFound = True
                        break

                # If no, clear and try again

    return returnPath


def createInitialMatrix(statePaths):
    """
    Generate an initial adjacency matrix for an automaton based on its transition paths.

    :param statePaths: A list of transition paths for the JFA.
    :return: A tuple containing the initial adjacency matrix and a list of loaded states in alphabetical order.
    """

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
    Find all possible paths from the startState to the endState in a graph represented by a list of transitions.

    :param transitions: A list of transitions in the format of [[stateX], [symbol], [stateY]].
    :param startState: The starting state of the path.
    :param endState: The ending state of the path.
    :param moves: The maximum number of moves allowed to reach the end state.
    :param path: (optional) A list to store the states in the path.
    :param symbols: (optional) A list to store the symbols on the edges of the path.
    :return: A list of paths, where each path is a list of states representing a path from startState to endState
             in the graph in n moves and a list of symbols on the "edges" of the path (symbols read),
             or an empty list if no such path exists.
    """

    # Initialize the path and symbols lists if they are not provided
    if path is None:
        path = [startState]
    if symbols is None:
        symbols = []

    # If no moves left, check if we have arrived at the end state
    if moves == 0:
        if startState == endState:
            # If the end state has been reached, return the path and symbols as a single-element list
            return [[path, symbols]]
        else:
            # If the end state has not been reached, return an empty list
            return []

    # If there is only one move left
    elif moves == 1:
        paths = []
        for stateX, symbol, stateY in transitions:
            if stateX == startState and stateY == endState:
                # If the edge connects the start and end states, add the new state and symbol to the path
                new_path = path + [endState]
                new_symbols = symbols + [symbol]
                # Add the path to the list of valid paths
                paths.append([new_path, new_symbols])
        # Return the list of valid paths
        return paths

    # If there are more than one moves left
    else:
        paths = []
        for stateX, symbol, stateY in transitions:
            if stateX == startState:
                # Generate a new path from state to state via transition
                new_path = path + [stateY]
                # Add symbol read of transition
                new_symbols = symbols + [symbol]
                # Recursively call findPath on the neighbor of the start state with moves decremented by 1
                sub_paths = findPath(transitions, stateY, endState, moves - 1, new_path, new_symbols)
                # Add each valid sub-path to the list of valid paths
                for sub_path in sub_paths:
                    paths.append(sub_path)
        # Return the list of valid paths
        return paths


def findNextSymbolPosition(currentReadSymbol, inputString, inputDict):
    """
    Find the index position of a given symbol in a string.

    :param currentReadSymbol: The symbol to search for in the input string.
    :param inputString: The string in which to search for the symbol.
    :param inputDict: A dictionary containing the number of occurrences of each symbol in the input string.
    :return: A tuple containing the modified string, the position of the next occurrence of the symbol, and the updated
             dictionary.
    """

    # Variables declaration
    outputString = ""
    symbolPosition = 0
    readSymbolIndex = -1
    symbolReached = False

    # Go through all symbols in input string
    for symbol in inputString:
        # If symbol is empty, write to output and continue
        if symbol == "_":
            outputString += "_"
            symbolPosition += 1

        # If symbol matches current symbol for first time, replace by empty, save index, flip flag and continue
        elif symbol == currentReadSymbol and not symbolReached:
            symbolReached = True
            outputString += "_"
            readSymbolIndex = symbolPosition
            continue

        # Otherwise write to output and continue
        else:
            outputString += symbol
            symbolPosition += 1

    # Check if value in dictionary and update
    if inputDict[currentReadSymbol] > 1:
        inputDict[currentReadSymbol] -= 1
    else:
        inputDict[currentReadSymbol] = 0

    return outputString, readSymbolIndex, inputDict
