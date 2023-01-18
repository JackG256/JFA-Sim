from customExceptions import InvalidAlphabetFormatError
from customExceptions import InvalidSymbolInAlphabetError


def filterMachineAlphabet(unfiltered):
    unfiltered = unfiltered.split(";")
    print(unfiltered)

    for symbol in unfiltered:
        if len(symbol) != 1:
            raise InvalidAlphabetFormatError()

    for symbol in unfiltered:
        if not symbol.isalpha():
            raise InvalidSymbolInAlphabetError()


    return unfiltered
