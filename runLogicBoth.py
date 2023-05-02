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
        formattedInputStr += f"// {key} ^ {inputDict[key]} "

    # Final string detail
    formattedInputStr += "//"

    return formattedInputStr
