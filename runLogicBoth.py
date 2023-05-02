def generateFormattedInputDictionary(inputDict):
    # For each key in formatted input string dictionary, put key in output string, and get occurence
    # value based on index of same key.

    formattedInputStr = ""
    for key in inputDict:
        formattedInputStr += f"// {key} ^ {inputDict[key]} "

    # Final string detail
    formattedInputStr += "//"

