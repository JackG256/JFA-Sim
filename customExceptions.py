class InvalidAlphabetFormatError(Exception):
    """Provided alphabet is written in an invalid format"""

    def __init__(self, symbolset, *args):
        super().__init__(args)
        self.symbolset = symbolset

    def __str__(self):
        return f"Inputted alphabet is written in an invalid format:\n" \
               f"\'{self.symbolset}\' is not a valid symbol"

    pass


class EmptyFieldError(Exception):
    """A required field is empty"""

    def __init__(self, fieldname, *args):
        super().__init__(args)
        self.fieldname = fieldname

    def __str__(self):
        return f"A field required for evaluation is empty: \'{self.fieldname}\'"

    pass


class InvalidSymbolInAlphabetError(Exception):
    """A provided symbol in input alphabet is not a valid letter or a number"""

    def __init__(self, symbol, *args):
        super().__init__(args)
        self.symbol = symbol

    def __str__(self):
        return f"\'{self.symbol}\' is not a valid letter or a number"

    pass


class InputSymbolNotInAlphabetError(Exception):
    """A symbol in input string is not included in the input alphabet"""

    def __init__(self, symbol, alphabet, *args):
        super().__init__(args)
        self.symbol = symbol
        self.alphabet = alphabet

    def __str__(self):
        return f"\'{self.symbol}\' is not a included in provided alphabet:<br>" \
               f"{self.alphabet}"

    pass


class StartStateNotFoundError(Exception):
    """A start state was not provided"""

    def __init__(self, *args):
        super().__init__(args)

    def __str__(self):
        return f"A start state was not provided in \'Machine states field\'"

    pass


class EndStateNotFoundError(Exception):
    """A start state was not provided"""

    def __init__(self, *args):
        super().__init__(args)

    def __str__(self):
        return f"An end state was not provided in \'Machine states field\'<br>" \
               f"Machine would automatically refuse any input"

    pass
