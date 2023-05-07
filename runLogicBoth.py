def generateFormattedInputDictionary(inputDict):
    """
    Returns a formatted string with occurence values

    :param inputDict: a dictionary of frequencies of symbols
    :return: formattedInputStr: a formatted string to be displayed
    """

    # For each key in formatted input string dictionary, put key in output string, and get occurence
    # value based on index of same key.

    formattedInputStr = ""
    for key in inputDict:
        formattedInputStr += f" {key} ^ {inputDict[key]} "
        formattedInputStr += f"//"

    # Cut last 2 dividing symbols

    formattedInputStr = formattedInputStr[:-2]
    return formattedInputStr


def createFormattedStringLabel(inputStringFull, readSymbols, lastPos):
    """
    Returns a coloured HTML format string to put in instance string label

    :param inputStringFull: Complete unedited string
    :param readSymbols: List of read symbols with positions
    :param lastPos: The position of last read symbol
    :return: labelString: coloured HTML format string
    """

    # Initialize/reinitialize the output string to put in label
    labelString = ""

    # Helping flag to prevent multiple green symbols
    markedGreen = False

    # Iterate over each symbol in the input string
    for i, symbol in enumerate(inputStringFull):
        # Check if the current symbol was just read by the JFA
        if [symbol, i] in readSymbols and i == lastPos and not markedGreen:
            # If the current symbol was just read, format it with green color,
            # then temporarily save the writen symbol and it's possition. (now obsolete)
            labelString += f"<span style='color:green'>{symbol}</span>"
            # symbolToUpdate = [symbol, i]

            # Flip the bool value to prevent multiple green symbols
            markedGreen = True

            # After that, skip this iteration
            continue

        # Check if the symbol has been read before by the JFA before
        if [symbol, i] in readSymbols:
            # If the symbol has been read before, format it with red color
            labelString += f"<span style='color:red'>{symbol}</span>"
        else:
            # If the symbol has not been read before, format it with black color
            labelString += f"<span style='color:black'>{symbol}</span>"

    return labelString


def returnRedInputString(inputStringFull):
    labelString = ""
    for symbol in inputStringFull:
        labelString += f"<span style='color:red'>{symbol}</span>"

    return labelString


def findNextJumps(jTransitions, currentState, inputString):
    """
    Finds the next possible jumps for the given current state and input string.

    :param jTransitions: List of transitions
    :param currentState: Current state name
    :param inputString: A string representing the input symbols.
    :return: A string containing a list of up to five possible jumps in the format
             "<source> -> <destination> (<symbol>)", separated by newlines. If there are no possible jumps,
              returns an empty string.
    """

    output = ""
    maxText = 5

    for entry in jTransitions:
        if entry[0] == currentState and entry[1] in inputString:
            output += f"{entry[0]} -> {entry[2]} ( {entry[1]} )\n"
            maxText -= 1
        if not maxText:
            break

    return output
