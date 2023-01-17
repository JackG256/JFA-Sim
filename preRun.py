import customExceptions.InvalidAlphabetFormat

def filterMachineAlphabet(unfiltered):
    unfiltered = unfiltered.split(";")
    print(unfiltered)

    for symbol in unfiltered:
        if len(symbol) != 1:
            raise customExceptions.InvalidAlphabetFormat

    for
    return unfiltered
