"""
Defines exceptions for the SQL package.

"""

# To the extent possible under law, the author(s) have dedicated all copyright and
# related and neighboring rights to this software to the public domain worldwide.
# This software is distributed without any warranty.
#     
# You should have received a copy of the CC0 Public Domain Dedication along with
# this software. If not, see <http://creativecommons.org/publicdomain/zero/1.0/>.

__all__ = [
    "ScanError",
    "ParseError",
    "syntax_error",
]

class ScanError(Exception):
    """
    Exception raised for errors whilst scanning input with a Scanner.

    Args:
        msg (str): the error message
        pos (int): the position in the input
    
    """

    def __init__(self, msg, pos):
        self.msg = msg
        self.pos = pos
        super().__init__("{} [near offset {}]".format(self.msg, self.pos))


class ParseError(Exception):
    """
    Exception raised for errors whilst parsing input.

    Args:
        msg (str): the error message
        tok (lexer.Token): the current token

    """

    def __init__(self, msg, tok):
        # Sanity checks
        if not isinstance(msg, str):
            raise TypeError("msg must be a string")
        self._msg = msg
        self._tok = tok
        super().__init__("{} [near {}, offset {}-{}]".format(self._msg, self._tok, self.start_position(), self.end_position()))

    def start_position(self):
        """Returns the start position (inclusive) of the error in the input."""
        return self._tok.start_position()

    def end_position(self):
        """Returns the final position (inclusive) of the error in the input."""
        return self._tok.end_position()

class InvalidConditionError(Exception):
    """
    Exception raised when a Condition fails to validate.
    
    Args:
        msg(str): the error message
    
    """
    def __init__(self, msg):
        # Sanity check
        if not isinstance(msg, str):
            raise TypeError("msg must be a string")
        self._msg = msg
        super().__init__(msg)
