"""
Provides tests for _parser.py

"""

# To the extent possible under law, the author(s) have dedicated all copyright and
# related and neighboring rights to this software to the public domain worldwide.
# This software is distributed without any warranty.
#     
# You should have received a copy of the CC0 Public Domain Dedication along with
# this software. If not, see <http://creativecommons.org/publicdomain/zero/1.0/>.

import unittest
from itertools import chain
from ..exceptions import ParseError, ScanError
from .. import parse_condition, parse_order, parse_query
from .. import condition, sort

class _parse_test:
    """
    Represents a test for the parser.
    
    Args:
        statement (str): the statement to parse
        condition (Condition): the condition that should result
        order (sort.OrderBy): the sort order that should result
        limit (Optional[int]): the limit

    """
    def __init__(self, statement, condition, order, limit):
        self.statement = statement
        self.condition = condition
        if isinstance(order, sort.Order):
            self.order = [order]
        else:
            self.order = order
        self.limit = limit

# condition_tests contains tests that just involve conditions
condition_tests = [
    _parse_test("", condition.TRUE, None, None),
    _parse_test("where is_smooth = True or is_canonical != False", 	condition.or_condition(condition.equal("is_smooth", True), condition.not_equal("is_canonical", False)), None, None),
	_parse_test("where vertices=\"[(0,1)\\t(1,0)\\t(-1,-1)]\"", condition.equal("vertices", "[(0,1)\t(1,0)\t(-1,-1)]"), None, None),
	_parse_test("number_of_points=3 and number_of_points = 4", condition.and_condition(condition.equal("number_of_points", 3), condition.equal("number_of_points", 4)), None, None),
	_parse_test("number_of_points=3 or number_of_points = 4 or number_of_points = 5", condition.or_condition(condition.equal("number_of_points", 3), condition.equal("number_of_points", 4), condition.equal("number_of_points", 5)), None, None),
	_parse_test("number_of_points in     (-3,4)", condition.in_condition("number_of_points", -3, 4), None, None),
	_parse_test("number_of_points    not  in     (3,4)", condition.not_in("number_of_points", 3, 4), None, None),
	_parse_test("number_of_points between    3   and  5", condition.between("number_of_points", 3, 5), None, None),
	_parse_test("number_of_points not  between    3   and  5", condition.not_between("number_of_points", 3, 5), None, None),
	_parse_test("where string_var = 'string with many escape sequences \\a \\b \\f \\n \\r \\t \\v'", condition.equal("string_var", "string with many escape sequences \a \b \f \n \r \t \v"), None, None),
	_parse_test("where very_large = 9223372036854775808", # this is MaxInt+1
		condition.equal("very_large", 9223372036854775808),
		None, None,
    ),
	_parse_test("where comp > 7", condition.greater_than("comp", 7), None, None),
	_parse_test("where comp >= 7", condition.greater_than_or_equal_to("comp", 7), None, None),
	_parse_test("where comp < 7", condition.less_than("comp", 7), None, None),
	_parse_test("where comp <= 7", condition.less_than_or_equal_to("comp", 7), None, None),
	_parse_test("where comp != 7", condition.not_equal("comp", 7), None, None),
	_parse_test("where comp = 7", condition.equal("comp", 7), None, None),
	_parse_test("true", condition.TRUE, None, None),
	_parse_test("false", condition.FALSE, None, None),
	_parse_test("not true", condition.FALSE, None, None),
	_parse_test("not false", condition.TRUE, None, None),
	_parse_test("(true)", condition.TRUE, None, None),
	_parse_test("not (false)", condition.TRUE, None, None),
	_parse_test("where x in ()", condition.FALSE, None, None),
	_parse_test("where x is true", condition.is_true("x"), None, None),
	_parse_test("where x is false", condition.is_false("x"), None, None),
	_parse_test("where x is not true", condition.is_false("x"), None, None),
	_parse_test("where x is not false", condition.is_true("x"), None, None),
]


# complex_tests contains tests that involve conditions, limits, and orders, where at least one of the limit and the order are non-trivial
complex_tests = [
    _parse_test(
        "where number_of_points <    6 and   (number_of_points >= 3.123) limit 0", condition.and_condition(condition.less_than("number_of_points", 6), condition.greater_than_or_equal_to("number_of_points", 3.123)), 
        None, 0
    ),
    _parse_test(
		"(a = true and b = true or c = true) or (a = false or b = false and c = false) limit 5000",
		condition.or_condition(
			condition.and_condition(condition.equal("a", True), condition.equal("b", True)), condition.equal("c", True),
			condition.equal("a", False), condition.and_condition(condition.equal("b", False), condition.equal("c", False))),
		None, 5000
    ),
    _parse_test(
		"(a is true and b is true or c = 4) and (a is false or b is not false and c = 7) limit 1000",
		condition.and_condition(
			condition.or_condition(condition.and_condition(condition.is_true("a"), condition.is_true("b")), condition.equal("c", 4)),
			condition.or_condition(condition.is_false("a"), condition.and_condition(condition.is_true("b"), condition.equal("c", 7))),
		),
		None, 1000
    ),
    _parse_test(
		"order by x",
		condition.TRUE,
		sort.ascending("x"), None
    ),
    _parse_test(
		"order by x limit 12",
		condition.TRUE,
		sort.ascending("x"), 12
    ),
    _parse_test(
		"order by x limit 9223372036854775807", # This is MaxInt64
		condition.TRUE,
		sort.ascending("x"), 9223372036854775807
    ),
    _parse_test(
		"order by foo asc, bar, cat desc limit 200",
		condition.TRUE,
		[sort.ascending("foo"),sort.ascending("bar"),sort.descending("cat")],
		200
    ),
]

# invalid_conditions contains conditions that should not parse.
invalid_conditions = [
	"where string_var = \"oops, I forgot to close the string",
	"where string_var = 'oops, I forgot to close the string",
	"where (string_var = 'I forgot to close the bracket'",
	"where (string_var = 'unexpected closing bracket'))",
	"where (string_var = 'invalid character in string \xE5'))",
	"where (string_var = \xE5'invalid character outside string'))",
	"where (string_var = 'invalid character in string\xE5'))",
	"where (string_var\xE5 = 'invalid character outside string'))",
	"where (string_var = 'bogus escape sequence \\h'))",
	"where int_var = --7",
	"where float_var = .7", # there needs to be a digit before the decimal point
	"where float_var = 0.7.55",
	"where float_var = 0.755oops",
	"where overflows = 18446744073709551616", # this is MaxUint64 + 1
	"where overflows = -9223372036854775809", # this is MinInt - 1
	"where not_an_operator !, 7",
	"where",
	"cheese",
	"where cheese",
	"where not cheese",
	"and",
	"where x in (and)",
	"where x in ('cheese' and)",
	"where x between 3 and and",
	"where x between or and 3",
	"where x between 3 'and' 4",
	"where x between 3 4",
	"where x is not (true)",
	"where x is not (false)",
	"where x is cheese",
	"where x < and",
	"where x not in (and)",
	"where x not in ('cheese' and)",
	"where x not between 3 and and",
	"where x not between or and 3",
	"where x not between 3 'and' 4",
	"where x not between 3 4",
	"where x notin ('fish')",
	"where x not and",
]

# invalid_orders contains orders that should not parse.
invalid_orders = [
	"order by x,",
	"order by x, and",
	"order by x and",
	"order by x desc and",
	"order x desc",
	"order by x asc order by y desc",
]

# invalid_limits contains limits that should not parse.
invalid_limits = [
	"limit",
	"limit -3",
	"limit 9223372036854775808", # this is MaxInt64 + 1
	"limit ,",
	"limit or",
	"limit 8 limit 8",
	"limit 8 limit 9",
]

def trim_prefix(s, prefix):
    """Returns s without prefix, or s if prefix is not present."""
    if s.startswith(prefix):
        return s[len(prefix):]
    return s

class TestParser(unittest.TestCase):

    def test_parse_query_error(self):
        self.assertRaisesRegex(
            ParseError, 
            "expected value \[near AND, offset 11-13\]", 
            lambda: parse_query("where x < and"))
    
    def test_parse_query(self):
        tests = chain(condition_tests, complex_tests)
        for t in tests:
            q = parse_query(t.statement)
            self.assertEqual(q.condition, t.condition)
            self.assertEqual(q.order, t.order)
            self.assertEqual(q.limit, t.limit)

    def test_parser_invalid_statements(self):
        statements = chain(invalid_conditions, invalid_orders, invalid_limits)
        for s in statements:
            self.assertRaises((ScanError, ParseError), parse_query, s)

    def test_parse_condition(self):
        for t in condition_tests:
			# Strip off the leading where, if present
            st = trim_prefix(t.statement, "where ")
            self.assertEqual(parse_condition(st), t.condition)
        # These statements should raise exceptions
        invalid_statements = chain(invalid_conditions, ["where x = 'perfectly_valid' and"])
        for s in invalid_statements:
            self.assertRaises((ScanError, ParseError), parse_condition, s)

    def test_parse_order(self):
        # Specify some tests
        tests = [
            _parse_test(
                "x",
                condition.TRUE,
                sort.ascending("x"), None,
            ),
            _parse_test(
                "foo asc, bar, cat desc",
                condition.TRUE,
                [
                    sort.ascending("foo"), 
                    sort.ascending("bar"), 
                    sort.descending("cat"),
				],
                None,
            ),
            _parse_test(
                "",
                condition.TRUE,
                None, None,
            ),
        ]
        # Run the tests
        for t in tests:
            order = parse_order(t.statement)
            self.assertEqual(t.order, order)
        # These statements should give errors
        x = [
            "order by x desc,",
            "order by x desc and",
            "order by x asc limit 12",
        ]
        invalid_statements = chain(invalid_orders, x)
        for s in invalid_statements:
            # strip off the leading order by, if present
            st = trim_prefix(s, "order by ")
            self.assertRaises(ParseError, parse_order, st)

