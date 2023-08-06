"""
Defines exceptions for the keyvalue package.

"""

# To the extent possible under law, the author(s) have dedicated all copyright and
# related and neighboring rights to this software to the public domain worldwide.
# This software is distributed without any warranty.
#     
# You should have received a copy of the CC0 Public Domain Dedication along with
# this software. If not, see <http://creativecommons.org/publicdomain/zero/1.0/>.

class TableClosedError(Exception):
    """Exception raised when trying to use a closed Table."""
    pass

class ConnectionClosedError(Exception):
    """Exception raised when trying to use a closed Connection."""
    pass

class ServerError(Exception):
    """
    Exception raised when a server error is encountered.
    
    Args:
        error (str):
            a string description of the error
        code (Optional[int]):
            the error code
        causes (Optional[List[str]]):
            additional information about the causes of the error
        cause_codes (Optional[List[int]]):
            error codes for the causes of the error

    """
    def __init__(self, error, code=None, causes=None, cause_codes=None):
        # Record the error
        if not isinstance(error, str):
            raise TypeError("the error must be a string")
        self.error = error
        # Record the error code
        if code is not None:
            if not isinstance(code, int):
                raise TypeError("the error code must be an int")
        self.code = code
        # Record the causes
        if not causes is None:
            if not isinstance(causes, list):
                raise TypeError("causes must be a list")
            for x in causes:
                if not isinstance(x, str):
                    raise TypeError("causes must be a list of strings")
        self.causes = causes
        # Record the cause_codes
        if not cause_codes is None:
            if not isinstance(cause_codes, list):
                raise TypeError("cause_codes must be a list")
            for x in cause_codes:
                if not isinstance(x, int):
                    raise TypeError("cause_codes must be a list of ints")
        self.cause_codes = cause_codes

    def __str__(self):
        s = "server error (code={}): {}".format(self.code, self.error)
        if not self.causes is None:
            s = s + "\ncauses: {}".format(self.causes)
        if not self.cause_codes is None:
            s = s + "\ncause codes: {}".format(self.cause_codes)
        return s