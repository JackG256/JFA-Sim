import numpy as np


def generateAdjacencyMatrix(jTransitions, iterationMax):
    initialMatrix, pathMatrix = createInitialMatrix(jTransitions)
    return initialMatrix, pathMatrix


def createInitialMatrix(statePaths):
    # Helping variable to store list of active states
    loadedStates = []

    # Find all active states based on Jump Transitions
    for entry in statePaths:
        if entry[0] not in loadedStates:
            loadedStates.append(entry[0])
        if entry[2] not in loadedStates:
            loadedStates.append(entry[2])

    # Get number of items in list
    xySize = len(loadedStates)

    # Create a 2D matrix with zeroes to store data into
    initialMatrix = [[0 for _ in range(xySize)] for _ in range(xySize)]
    # Create a 2D matrix with empty string spaces to store symbol data into
    pathMatrix = [["" for _ in range(xySize)] for _ in range(xySize)]

    listOfPaths = []

    for i, stateY in enumerate(loadedStates):
        for j, stateX in enumerate(loadedStates):
            for entry in statePaths:
                if stateY == entry[0] and stateX == entry[2]:
                    initialMatrix[i][j] += 1
                    listOfPaths.append([i, j, entry[1]])

    for entry in listOfPaths:
        if pathMatrix[entry[0]][entry[1]] == "":
            pathMatrix[entry[0]][entry[1]] += entry[2]
        else:
            pathMatrix[entry[0]][entry[1]] += f"#{entry[2]}"

    return initialMatrix, pathMatrix

