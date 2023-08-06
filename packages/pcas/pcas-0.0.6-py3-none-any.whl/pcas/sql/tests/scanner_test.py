"""
Provides tests for _scanner.py

"""

# To the extent possible under law, the author(s) have dedicated all copyright and
# related and neighboring rights to this software to the public domain worldwide.
# This software is distributed without any warranty.
#     
# You should have received a copy of the CC0 Public Domain Dedication along with
# this software. If not, see <http://creativecommons.org/publicdomain/zero/1.0/>.

import unittest
from .._scanner import _Scanner
from .._lexer import _Tokeniser
from ..exceptions import ScanError


class TestScanner(unittest.TestCase):

    def test_scanner_error(self):
        s = "a perfectly valid string"
        t = _Tokeniser(_Scanner(s))
        next(t) # no exception
        s = "\u0394 a string with an invalid leading character"
        t = _Tokeniser(_Scanner(s))
        self.assertRaisesRegex(ScanError, "invalid character \[near offset 0\]", lambda: next(t))

    def test_position(self):
        t = _Scanner("")
        self.assertEqual(t.position(), 0)
        s = "a valid string"
        self.assertEqual(t.position(), 0)


if __name__ == '__main__':
    unittest.main()