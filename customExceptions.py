class InvalidAlphabetFormatError(Exception):
    """Provided alphabet is written in an invalid format"""

    def __init__(self, symbolset, *args):
        super().__init__(args)
        self.symbolset = symbolset

    def __str__(self):
        return f"Input alphabet is written in an invalid format:\n" \
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


class InvalidDeterministicFormat(Exception):
    """Provided jump transitions are invalid for deterministic approach"""

    def __init__(self, state, *args):
        super().__init__(args)
        self.state = state

    def __str__(self):
        return f"Provided configuration of jump transitions doesn't behave deterministically:" \
               f"<br>The state {self.state} has too many outward transitions of same symbol"

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
        return f"\'{self.symbol}\' is not included in provided alphabet:<br>" \
               f"{self.alphabet}"

    pass


class StartStateNotFoundError(Exception):
    """A start state was not provided"""

    def __init__(self, *args):
        super().__init__(args)

    def __str__(self):
        return f"A start state was not provided in \'Start State Combobox\'"

    pass


class EndStateNotFoundError(Exception):
    """A start state was not provided"""

    def __init__(self, *args):
        super().__init__(args)

    def __str__(self):
        return f"An end state was not provided in \'End States Selection\'<br>" \
               f"Machine would automatically refuse any input"

    pass


class StateDoesNotExistError(Exception):
    """A state provided in jump does not exist"""

    def __init__(self, state, *args):
        super().__init__(args)
        self.state = state

    def __str__(self):
        return f"A state specified in transition function does not exist:  \'{self.state}\'<br>"

    pass


class SymbolDoesNotExistError(Exception):
    """A symbol provided in jump does not exist"""

    def __init__(self, symbol, *args):
        super().__init__(args)
        self.symbol = symbol

    def __str__(self):
        return f"A symbol specified in transition function does not exist:  \'{self.symbol}\'<br>"

    pass


class NoJumpToPerform(Exception):
    """Provided state has no jump to perform"""

    def __init__(self, state, *args):
        super().__init__(args)
        self.state = state

    def __str__(self):
        return f"Current machine state has no jump to perform: '{self.state}'"

    pass


class NoAcceptPathFound(Exception):
    """No accepting path exists for current non-deterministic setup"""

    def __init__(self, *args):
        super().__init__(args)

    def __str__(self):
        return f"Current automata configuration contains no accepting path.\n<b>String automatically refused!<b>"
