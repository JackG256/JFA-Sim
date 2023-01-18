class InvalidAlphabetFormatError(Exception):
    """Provided alphabet is written in an invalid format"""
    pass


class InvalidSymbolInAlphabetError(Exception):
    """A provided symbol in input alphabet is not a valid letter"""
    pass
