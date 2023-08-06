"""
Defines a scanner for parsing SQL-formatted queries.

"""

# To the extent possible under law, the author(s) have dedicated all copyright and
# related and neighboring rights to this software to the public domain worldwide.
# This software is distributed without any warranty.
#     
# You should have received a copy of the CC0 Public Domain Dedication along with
# this software. If not, see <http://creativecommons.org/publicdomain/zero/1.0/>.

class _Scanner:
    """
    Scanner defines a scanner for parsing SQL-formatted queries.
    
    Args:
        s (str): the underlying string
        
    """
    def __init__(self, s):
        # Record the string
        self._itr = iter(s)
        # Record the position in the input
        self._pos = 0
        # Initialise an (empty) buffer of pushed characters
        self._buf = []
        # buf_idx holds the position of the first empty entry in the buffer
        self._buf_idx = 0

    def __iter__(self):
        return self
    
    def __next__(self):
        if self._buf_idx != 0:
            # We have characters in the buffer, so use the last one of these
            r = self._buf[self._buf_idx-1]
            self._buf_idx -= 1
            self._pos += 1
            return r
        # Read and return the next character
        r = next(self._itr)
        self._pos += 1
        return r

    def push(self, c):
        """
        Push the character c back onto the input.
        
        """
        # Sanity checks
        if type(c) != str or len(c) != 1:
            raise TypeError("illegal character")
        # Add c to the buffer
        if self._buf_idx < len(self._buf):
            self._buf[self._buf_idx] = c
        else:
            self._buf.append(c)
        self._buf_idx += 1
        self._pos-= 1
    
    def position(self):
        """
        Return the current position in the input.
        
        """
        return self._pos