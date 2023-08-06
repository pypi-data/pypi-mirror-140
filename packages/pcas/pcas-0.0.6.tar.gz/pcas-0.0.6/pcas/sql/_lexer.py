"""
Defines a lexer for parsing SQL-formatted queries.

"""

# To the extent possible under law, the author(s) have dedicated all copyright and
# related and neighboring rights to this software to the public domain worldwide.
# This software is distributed without any warranty.
#     
# You should have received a copy of the CC0 Public Domain Dedication along with
# this software. If not, see <http://creativecommons.org/publicdomain/zero/1.0/>.

from ._scanner import _Scanner
from .exceptions import ScanError

from enum import Enum
import abc
import sys

_INT64_MIN = -9223372036854775808 
_INT64_MAX =  9223372036854775807
_UINT64_MAX = 18446744073709551615

class _Type(Enum):
    """The valid token types."""
    STRING = 1
    INT64 = 2
    UINT64 = 3
    FLOAT64 = 4
    TRUE = 5
    FALSE = 6
    OPENBRACKET = 7
    CLOSEBRACKET = 8
    COMMA = 9
    WHERE = 10
    IS = 11
    EQ = 12
    LT = 13
    GT = 14
    LE = 15
    GE = 16
    NE = 17
    NOT = 18
    AND = 19
    OR = 20
    IN = 21
    BETWEEN = 22
    ORDER = 23
    BY = 24
    ASC = 25
    DESC = 26
    LIMIT = 27
    EOF = 28

    def __str__(self) -> str:
        # strLookup defines the string representations of Types
        strLookup = {
            _Type.STRING: "STRING",
            _Type.INT64: "INT",
            _Type.UINT64: "UINT",
            _Type.FLOAT64: "FLOAT",
            _Type.TRUE: "TRUE",
            _Type.FALSE: "FALSE",
            _Type.OPENBRACKET: "(",
            _Type.CLOSEBRACKET: ")",
            _Type.COMMA: ",",
            _Type.WHERE: "WHERE",
            _Type.IS: "IS",
            _Type.EQ: "=",
            _Type.LT: "<",
            _Type.GT: ">",
            _Type.LE: "<=",
            _Type.GE: ">=",
            _Type.NE: "!=",
            _Type.NOT: "NOT",
            _Type.AND: "AND",
            _Type.OR: "OR",
            _Type.IN: "IN",
            _Type.BETWEEN: "BETWEEN",
            _Type.ORDER: "ORDER",
            _Type.BY: "BY",
            _Type.ASC: "ASC",
            _Type.DESC: "DESC",
            _Type.LIMIT: "LIMIT",
            _Type.EOF: "<eof>",
        }
        if not self in strLookup:
            return "<unknown type>"
        return strLookup[self]


class _Token(metaclass=abc.ABCMeta):
    """Defines the interface representing a token."""

    def __init__(self, start, finish):
        self.start = start
        self.finish = finish
    
    @abc.abstractmethod
    def type(self):
        """Returns the token type"""

    def start_position(self):
        """Returns the initial position (inclusive) of this token."""
        return self.start
    
    def end_position(self):
        """Returns the final position (inclusive) of this token."""
        return self.finish

    @abc.abstractmethod
    def is_value():
        """Returns true if and only if the token could represent a value."""
    
    @abc.abstractmethod
    def value():
        """The value associated with this token, if any."""


class _StringToken(_Token):
    """Represents a string."""

    def __init__(self, start, finish, val):
        if not isinstance(val, str):
            raise TypeError("value must be a string")
        self.val = val
        super().__init__(start, finish)

    def __str__(self):
        return '\"' + self.val.encode('unicode-escape').decode('utf-8') + '\"'

    def type(self):
        return _Type.STRING
    
    def is_value(self):
        return True
    
    def value(self):
        return self.val


class _BoolToken(_Token):
    """Represents a boolean."""

    def __init__(self, start, finish, val):
        if not isinstance(val, bool):
            raise TypeError("value must be a boolean")
        self.val = val
        super().__init__(start, finish)

    def __str__(self):
        return str(self.val).upper()

    def type(self):
        if self.val:
            return _Type.TRUE
        return _Type.FALSE
    
    def is_value(self):
        return True
    
    def value(self):
        return self.val

class _Int64Token(_Token):
    """
    Represents a 64-bit integer.
    
    Raises:
        ValueError:
            if the integer will not fit into a 64-bit integer
    """

    def __init__(self, start, finish, val):
        if not isinstance(val, int):
            raise TypeError("value must be an integer")
        if not _INT64_MIN <= val <= _INT64_MAX:
            raise ValueError("value out of range")
        self.val = val
        super().__init__(start, finish)

    def __str__(self):
        return str(self.val)

    def type(self):
        return _Type.INT64
    
    def is_value(self):
        return True
    
    def value(self):
        return self.val


class _Uint64Token(_Token):
    """
    Represents a 64-bit unsigned integer.
    
    Raises:
        ValueError:
            if the integer will not fit into a 64-bit unsigned integer
    """

    def __init__(self, start, finish, val):
        if not isinstance(val, int):
            raise TypeError("value must be an integer")
        if not 0 <= val <= _UINT64_MAX:
            raise ValueError("value out of range")
        self.val = val
        super().__init__(start, finish)

    def __str__(self):
        return str(self.val)

    def type(self):
        return _Type.UINT64
    
    def is_value(self):
        return True
    
    def value(self):
        return self.val


class _Float64Token(_Token):
    """
    Represents a 64-bit floating-point number.
    
    Raises:
        ValueError:
            if the number will not fit into a 64-bit float
    """

    def __init__(self, start, finish, val):
        if not isinstance(val, float):
            raise TypeError("value must be a floating-point value")
        # We check the range because val could be denormalized.
        if not -sys.float_info.max <= val <= sys.float_info.max:
            raise ValueError("value out of range")
        self.val = val
        super().__init__(start, finish)

    def type(self):
        return _Type.FLOAT64
    
    def __str__(self):
        return str(self.val)

    def is_value(self):
        return True
    
    def value(self):
        return self.val


class _CommaToken(_Token):
    """Represents a comma."""

    def __init__(self, start, finish):
        super().__init__(start, finish)

    def __str__(self):  
        return ","

    def type(self):
        return _Type.COMMA
    
    def is_value(self):
        return False
    
    def value(self):
        return None


class _WordToken(_Token):
    """
    Represents a reserved word.
    
    Raises:
        ValueError:
            an unknown reserved word was encountered

    """

    def __init__(self, start, finish, word):
        if not isinstance(word, str):
            raise TypeError("word must be a string")
        # typeLookup records the type of each reserved word
        typeLookup = {
            "WHERE": _Type.WHERE,
            "IS": _Type.IS,
            "NOT": _Type.NOT,
            "AND": _Type.AND,
            "OR": _Type.OR,
            "IN": _Type.IN,
            "BETWEEN": _Type.BETWEEN,
            "ORDER": _Type.ORDER,
            "BY": _Type.BY,
            "ASC": _Type.ASC,
            "DESC": _Type.DESC,
            "LIMIT": _Type.LIMIT,
            "=": _Type.EQ,
            ">": _Type.GT,
            "<": _Type.LT,
            ">=": _Type.GE,
            "<=": _Type.LE,
            "!=": _Type.NE,
            "(": _Type.OPENBRACKET,
            ")": _Type.CLOSEBRACKET,
        }
        if not word in typeLookup:
            raise ValueError("unknown reserved word: {}".format(word))
        # We store the type as the value of the token
        self.val = typeLookup[word]
        super().__init__(start, finish)

    def __str__(self):
        return str(self.val)

    def type(self):
        return self.val
    
    def is_value(self):
        return False
    
    def value(self):
        return None


class _EOFToken(_Token):
    """Represents the end of the string or file."""

    def __init__(self, start, finish):
        super().__init__(start, finish)

    def __str__(self):
        return "EOF"

    def type(self):
        return _Type.EOF
    
    def is_value(self):
        return False
    
    def value(self):
        return None


class _Tokeniser:
    """
    Tokeniser tokenises a _Scanner
    
    Args:
        s: the underlying _Scanner
        
    """
    def __init__(self, s):
        if not isinstance(s,_Scanner):
            raise TypeError("s must be a scanner.Scanner")
        # Record the scanner
        self._s = s
        # Initialise an (empty) buffer of pushed tokens
        self._buf = []
        # buf_idx holds the position of the first empty entry in the buffer
        self._buf_idx = 0

    def __iter__(self):
        return self
    
    def __next__(self):
        """
        Returns the next token.
        
        Raises:
            ScanError:
                an invalid character was encountered
        """
        if self._buf_idx != 0:
            # There are tokens in the buffer, so return the last one
            tok = self._buf[self._buf_idx-1]
            self._buf_idx -= 1
            return tok
        # Fetch the next non-space character
        c = " "
        while c.isspace():
            try:
                c = next(self._s)
            except StopIteration:
                pos = self._s.position()
                return _EOFToken(pos, pos)
        # Switch on the character
        if c == '(' or c == ')':
            pos = self._s.position()
            return _WordToken(pos,pos,c)
        elif c == ',':
            pos = self._s.position()
            return _CommaToken(pos, pos)
        elif c == '"' or c == '\'':
            self._s.push(c)
            return self._quoted_string()
        elif c == '=' or c == '<' or c == '>' or c == '!':
            self._s.push(c)
            return self._operator()
        else:
            self._s.push(c)
            if c == '-' or c.isdigit():
                return self._number()
            elif "a" <= c <= "z" or "A" <= c <= "Z":
                return self._word()
            raise ScanError("invalid character", self._s.position())

    def push(self, t):
        """Pushes the token t back on to the input."""
        if not isinstance(t, _Token):
            raise TypeError("t must be a Token")
        if self._buf_idx < len(self._buf):
            self._buf[self._buf_idx] = t
        else:
            self._buf.append(t)
        self._buf_idx += 1
    
    def _quoted_string(self):
        """
        Returns the token corresponding to a quoted string.

        Assumes that the next character is the opening quote.

        Raises:
            ScanError:
                an illegal character or unexpected EOF was encountered

        """
        # Read the opening quote
        delim = next(self._s)
        start_pos = self._s.position()
        # Start reading the string
        pieces = []
        isEscaped = False
        while True:
            # Read the next character
            try:
                c = next(self._s)
            except StopIteration:
                raise ScanError("illegal EOF in string", self._s.position())
            # Are we done?
            if not isEscaped and c == delim:
                end_pos = self._s.position()
                word = "".join(pieces)
                return _StringToken(start_pos, end_pos, word)
            # Handle escaping
            if isEscaped:
                if c == '"' or c == '\'' or c == '\\':
                    pass
                elif c == 'a':
                    c = '\a'
                elif c == 'b':
                    c = '\b'
                elif c == 'f':
                    c = '\f'
                elif c == 'n':
                    c = '\n'
                elif c == 'r':
                    c = '\r'
                elif c == 't':
                    c = '\t'
                elif c == 'v':
                    c = '\v'
                else:
                    msg = "unknown escape sequence: \\{}".format(c)
                    raise ScanError(msg, self._s.position())
                isEscaped = False
            elif c == '\\':
                isEscaped = True
            # Add the character
            if not isEscaped:
                pieces.append(c)

    def _convert_float(self, s, start, finish):
        """
        Converts the given string to a Token of type FLOAT64.

        Args:
            s: the string
            start: the start position of the token
            end: the end position of the token
        
        Raises:
            ScanError:
                if parsing the floating point number fails

        """
        try:
            f = float(s)
        except ValueError:
            msg = "unable to parse floating point number: {}".format(s)
            raise ScanError(msg, start)
        return _Float64Token(start, finish, f)

    def _convert_integer(self, s, start, finish):
        """
        Converts the given string to a Token of type INT64 or UINT64.
        
        Args:
            s: the string to convert
            start: the start position of the token
            end: the end position of the token

        Raises:
            ScanError:
                if parsing the integer fails

        """
        try:
            n = int(s)
        except ValueError:
            msg = "unable to parse integer: {}".format(s)
            raise ScanError(msg, start)
        if _INT64_MIN <= n <= _INT64_MAX:
            return _Int64Token(start, finish, n)
        elif 0 <= n <= _UINT64_MAX:
            return _Uint64Token(start, finish, n)
        msg = "integer overflow: {}".format(s)
        raise ScanError(msg, start)

    def _number(self):
        """
        Returns the Token corresponding to a number.

        Assumes the next character to be read is either a digit or '-'.
        
        Raises:
            ScanError:
                if parsing the number fails

        """
        # Read the first character
        c = next(self._s)
        start = self._s.position()
        hasDigit = (c != '-')
        hasPeriod = False
        # Parse the remainder of the number
        digits = []
        try:
            while True:
                # Record the character
                digits.append(c)
                # Read the next character
                c = next(self._s)
                # Sanity checks
                if c == '-':
                    raise ScanError("malformed number", start)
                elif c == '.':
                    if hasPeriod or not hasDigit:
                        raise ScanError("malformed number", start)
                    hasPeriod = True
                elif c.isdigit():
                    hasDigit = True
                else:
                    # Replace the character and break out of the digit processing loop
                    self._s.push(c)
                    break

        except StopIteration:
            pass
        # We've reached the end of the number
        s = "".join(digits)
        finish = self._s.position()
        # Attempt to convert the string into a number
        if hasPeriod:
            return self._convert_float(s, start, finish)
        else:
            return self._convert_integer(s, start, finish)

    def _as_reserved_word(self, s, start, finish):
        """
        Returns the Token corresponding to the reserved word s, or None if 
        s is not a reserver word.
        
        Args:
            s: the string to analyse
            start: the start position of the token
            finish: the end position of the token
        
        """
        s = s.upper()
        if s == "TRUE":
            return _BoolToken(start, finish, True)
        elif s == "FALSE":
            return _BoolToken(start, finish, False)
        elif s == "WHERE":
            return _WordToken(start, finish, s)
        elif s == "IS":
            return _WordToken(start, finish, s)
        elif s == "NOT":
            return _WordToken(start, finish, s)
        elif s == "AND":
            return _WordToken(start, finish, s)
        elif s == "OR":
            return _WordToken(start, finish, s)
        elif s == "IN":
            return _WordToken(start, finish, s)
        elif s == "BETWEEN":
            return _WordToken(start, finish, s)
        elif s == "ORDER":
            return _WordToken(start, finish, s)
        elif s == "BY":
            return _WordToken(start, finish, s)
        elif s == "ASC":
            return _WordToken(start, finish, s)
        elif s == "DESC":
            return _WordToken(start, finish, s)
        elif s == "LIMIT":
            return _WordToken(start, finish, s)
        # This is not a reserved word
        return None
    
    def _word(self):
        """
        Returns the token corresponding to the next word.
        
        Assumes that the first character lies in a-zA-Z.
        Subsequent characters must lie in a-zA-Z0-9_
        
        """
        # Read the first character
        c = next(self._s)
        start = self._s.position()
        # Parse the remainder of the word
        chars = []
        try:
            while True:
                chars.append(c)
                # Read the next character
                c = next(self._s)
                # Are we done?
                if not ('a' <=c <= 'z' or 'A' <= c <= 'Z' or 
                        '0' <= c <= '9' or c == '_'):
                    self._s.push(c)
                    break
        except StopIteration:
            pass
        # Is this a reserved word? Otherwise it is a string.
        s = "".join(chars)
        finish = self._s.position()
        tok = self._as_reserved_word(s, start, finish)
        if tok is not None:
            return tok
        return _StringToken(start, finish, s)
    
    def _operator(self):
        """
        Returns the Token corresponding to the next operator.
        
        Assumes that the first character is one of '=', '>', '<', '!'.
        
        Raises:
            ScanError:
                an unknown operator was encountered

        """
        # Read the first character
        c1 = next(self._s)
        start = self._s.position()
        # Are we done?
        if c1 == '=':
            return _WordToken(start, start, c1)
        # Read the second character
        c2 = next(self._s)
        finish = self._s.position()
        # Return the operator
        if c2 != '=':
            self._s.push(c2)
            if c1 == '>' or c1 == '<':
                return _WordToken(start, start, c1)
            elif c1 == '!':
                raise ScanError("unknown operator", start)
        if c1 == '>' or c1 == '<' or c1 == '!':
            return _WordToken(start, finish, c1+c2)
        raise ScanError("unknown operator", start)

