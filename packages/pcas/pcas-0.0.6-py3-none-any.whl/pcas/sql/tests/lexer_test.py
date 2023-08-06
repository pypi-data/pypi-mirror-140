"""
Provides tests for _lexer.py

"""

# To the extent possible under law, the author(s) have dedicated all copyright and
# related and neighboring rights to this software to the public domain worldwide.
# This software is distributed without any warranty.
#     
# You should have received a copy of the CC0 Public Domain Dedication along with
# this software. If not, see <http://creativecommons.org/publicdomain/zero/1.0/>.

import unittest
from .._scanner import _Scanner
from .._lexer import _Tokeniser, _Type

class TestLexer(unittest.TestCase):

    def test_lexer(self):
        # The input 
        statements = [
            "where is_smooth = True or is_canonical != False",
            "vertices=\"[(0,1)\t(1,0)\\t(-1,-1)]\"",
            "number_of_points=3 and number_of_points = 4",
            "number_of_points=3 or number_of_points = 4 or number_of_points = 5",
            "number_of_points in     (-3,4)",
            "number_of_points    not  in     (3,4)",
            "number_of_points between    3   and  5",
            "number_of_points not  between    3   and  5",
            "number_of_points <    6 and   (number_of_points >= 3.123)",
            "(a = true and b = true or c = true) or (a = false or b = false and c = false)",
            "(a is true and b is true or c = 4) and (a is false or b is not false and c = 7)",
            "order by foo asc, bar, cat desc limit 6",
        ]
        # The expected output
        types = [
            [_Type.WHERE, _Type.STRING, _Type.EQ, _Type.TRUE, _Type.OR, _Type.STRING, _Type.NE, _Type.FALSE],
            [_Type.STRING, _Type.EQ, _Type.STRING],
            [_Type.STRING, _Type.EQ, _Type.INT64, _Type.AND, _Type.STRING, _Type.EQ, 
            _Type.INT64],
            [_Type.STRING, _Type.EQ, _Type.INT64, _Type.OR, _Type.STRING, _Type.EQ, _Type.INT64, _Type.OR, _Type.STRING, _Type.EQ, _Type.INT64],
            [_Type.STRING, _Type.IN, _Type.OPENBRACKET, _Type.INT64, _Type.COMMA, _Type.INT64, _Type.CLOSEBRACKET],
            [_Type.STRING, _Type.NOT, _Type.IN, _Type.OPENBRACKET, _Type.INT64, _Type.COMMA, _Type.INT64, _Type.CLOSEBRACKET],
            [_Type.STRING, _Type.BETWEEN, _Type.INT64, _Type.AND, _Type.INT64],
            [_Type.STRING, _Type.NOT, _Type.BETWEEN, _Type.INT64, _Type.AND, _Type.INT64],
            [_Type.STRING, _Type.LT, _Type.INT64, _Type.AND, _Type.OPENBRACKET, _Type.STRING, _Type.GE, _Type.FLOAT64, _Type.CLOSEBRACKET],
            [_Type.OPENBRACKET, _Type.STRING, _Type.EQ, _Type.TRUE, _Type.AND, _Type.STRING, _Type.EQ, _Type.TRUE, _Type.OR, _Type.STRING, _Type.EQ, _Type.TRUE, _Type.CLOSEBRACKET, _Type.OR, _Type.OPENBRACKET, _Type.STRING, _Type.EQ, _Type.FALSE, _Type.OR, _Type.STRING, _Type.EQ, _Type.FALSE, _Type.AND, _Type.STRING, _Type.EQ, _Type.FALSE, _Type.CLOSEBRACKET],
            [_Type.OPENBRACKET, _Type.STRING, _Type.IS, _Type.TRUE, _Type.AND, _Type.STRING, _Type.IS, _Type.TRUE, _Type.OR, _Type.STRING, _Type.EQ, _Type.INT64, _Type.CLOSEBRACKET, _Type.AND, _Type.OPENBRACKET, _Type.STRING, _Type.IS, _Type.FALSE, _Type.OR, _Type.STRING, _Type.IS, _Type.NOT, _Type.FALSE, _Type.AND, _Type.STRING, _Type.EQ, _Type.INT64, _Type.CLOSEBRACKET],
            [_Type.ORDER, _Type.BY, _Type.STRING, _Type.ASC, _Type.COMMA, _Type.STRING, _Type.COMMA, _Type.STRING, _Type.DESC, _Type.LIMIT, _Type.INT64],
        ]
        self.assertEqual(len(statements), len(types), "mismatched test data")
        # Run the tests
        for s, t in zip(statements, types):
            T = _Tokeniser(_Scanner(s))
            idx = 0
            for tok in T:
                if tok.type() == _Type.EOF:
                    break
                self.assertEqual(tok.type(), t[idx], 
                                "test: {}, offset: {}".format(s, idx+1))
                idx += 1
                
    def test_string_and_value(self):
        statements = [
            "where is_smooth = True or is_canonical != False",
            "12 -12 9223372036854775807 9223372036854775808 1.234 -1.234 < <= > >= = != , ( ) AND NOT BETWEEN IS ASC DESC LIMIT IN ORDER BY",
            "'fish' fish \"fish\"",
            "fish in 'wrapping paper'",
        ]
        types = [
            [_Type.WHERE, _Type.STRING, _Type.EQ, _Type.TRUE, _Type.OR, _Type.STRING, _Type.NE, _Type.FALSE],
            [_Type.INT64, _Type.INT64, _Type.INT64, _Type.UINT64, _Type.FLOAT64, _Type.FLOAT64, _Type.LT, _Type.LE, _Type.GT, _Type.GE, _Type.EQ, _Type.NE, _Type.COMMA, _Type.OPENBRACKET, _Type.CLOSEBRACKET, _Type.AND, _Type.NOT, _Type.BETWEEN, _Type.IS, _Type.ASC, _Type.DESC, _Type.LIMIT, _Type.IN, _Type.ORDER, _Type.BY],
            [_Type.STRING, _Type.STRING, _Type.STRING],
            [_Type.STRING, _Type.IN, _Type.STRING],
        ]
        type_strings = [
            ["WHERE", "STRING", "=", "TRUE", "OR", "STRING", "!=", "FALSE"],
            ["INT", "INT", "INT", "UINT", "FLOAT", "FLOAT", "<", "<=", ">", ">=", "=", "!=", ",", "(", ")", "AND", "NOT", "BETWEEN", "IS", "ASC", "DESC", "LIMIT", "IN", "ORDER", "BY"],
            ["STRING", "STRING", "STRING"],
            ["STRING", "IN", "STRING"],
        ]
        S = [
            ["WHERE", "\"is_smooth\"", "=", "TRUE", "OR", "\"is_canonical\"", "!=", "FALSE"],
            ["12", "-12", "9223372036854775807", "9223372036854775808", "1.234", "-1.234", "<", "<=", ">", ">=", "=", "!=", ",", "(", ")", "AND", "NOT", "BETWEEN", "IS", "ASC", "DESC", "LIMIT", "IN", "ORDER", "BY"],
            ["\"fish\"", "\"fish\"", "\"fish\""],
            ["\"fish\"", "IN", "\"wrapping paper\""],
        ]
        is_values = [
            [False, True, False, True, False, True, False, True],
            [True, True, True, True, True, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False],
            [True, True, True],
            [True, False, True],
        ]
        values = [
            [None, "is_smooth", None, True, None, "is_canonical", None, False],
		    [12, -12, 9223372036854775807, 9223372036854775808, 1.234, -1.234, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
		    ["fish", "fish", "fish"],
		    ["fish", None, "wrapping paper"],
        ]
        # Sanity checks
        self.assertEqual(len(statements), len(types), "mismatched test data")
        self.assertEqual(len(statements), len(type_strings), "mismatched test data")
        self.assertEqual(len(statements), len(S), "mismatched test data")
        self.assertEqual(len(statements), len(is_values), "mismatched test data")
        self.assertEqual(len(statements), len(values), "mismatched test data")
        # Run the tests
        eof = None
        for s, t, s_str, t_str, is_val, val in zip(statements, types, S, type_strings, is_values, values):
            T = _Tokeniser(_Scanner(s))
            idx = 0
            for tok in T:
                if tok.type() == _Type.EOF:
                    eof = tok
                    break
                msg = "test: {}, offset: {}".format(s, idx+1)
                self.assertEqual(tok.type(), t[idx], msg)
                self.assertEqual(str(tok), s_str[idx], msg)
                self.assertEqual(str(tok.type()), t_str[idx], msg)
                self.assertEqual(tok.is_value(), is_val[idx], msg)
                self.assertEqual(tok.value(), val[idx], msg)
                idx += 1
        msg = "test: {}, at EOF".format(s)
        self.assertEqual(eof.type(), _Type.EOF, msg)
        self.assertEqual(str(eof.type()), "<eof>", msg)
        self.assertEqual(str(eof), "EOF", msg)
        self.assertEqual(eof.is_value(), False, msg)
        self.assertEqual(eof.value(), None, msg)
        
if __name__ == '__main__':
    unittest.main()