"""
Defines a parser for parsing SQL-formatted queries.

See the package docstring for the SQL format.
"""

# To the extent possible under law, the author(s) have dedicated all copyright and
# related and neighboring rights to this software to the public domain worldwide.
# This software is distributed without any warranty.
#     
# You should have received a copy of the CC0 Public Domain Dedication along with
# this software. If not, see <http://creativecommons.org/publicdomain/zero/1.0/>.

from ._scanner import _Scanner
from .exceptions import ParseError
from ._lexer import _INT64_MAX, _Token, _Tokeniser, _Type
from . import sort, condition


class Query:
	"""
	Describes a query.
	
	Args:
		cond (condition.Condition): 
			the condition
		order (Optional[Union[sort.Order,Iterable[sort.Order]]]): 
			the sort order
		limit (Optional[int]): 
			the limit

	"""
	def __init__(self, cond, order=None, limit=None):
		# Sanity check
		if not isinstance(cond, condition.Condition):
			raise TypeError("expected a condition.Condition")
		# Do we have a sort order?
		self.order = None
		if not order is None:
			# In this case self.order is a list of sort.Orders
			if isinstance(order, sort.Order):
				self.order = [order]
			else:
				self.order = []
				for x in order:
					if not isinstance(x, sort.Order):
						raise TypeError("expected a sort.Order")
					self.order.append(x)
		# Do we have a limit
		if not limit is None:
			if not isinstance(limit, int):
				raise TypeError("expected an integer")
		self.limit = limit
		# Record the condition 
		self.condition = cond


def _new_query():
	"""Returns a new, empty query."""
	return Query(condition.TRUE)

################################################################################
# Local functions
################################################################################

def _where_loop(t):
	"""
	Parses a stream of tokens into a WHERE condition.
	
	Args:
		t (_Tokeniser): the underlying tokeniser

	Raises:
		ParseError: 
			a syntax error occurred
	    ScanError:
    	    an invalid character was encountered

	"""
	if not isinstance(t, _Tokeniser):
		raise TypeError("expected a _Tokeniser")
	# conds holds the condition.Conditions that need OR-ing together
	conds = []
	# parse a condition
	cond = _parse_condition(t)
	conds.append(cond)
	# loop over the conditions
	while True:
		# Read the next token
		tok = next(t)
		# Switch on the token type
		tt = tok.type()
		if (
			tt == _Type.CLOSEBRACKET or
			tt == _Type.ORDER or
			tt == _Type.LIMIT or
			tt == _Type.EOF
		):
			t.push(tok)
			return condition.or_condition(*conds)
		elif (
			tt == _Type.OR or
			tt == _Type.AND
		):
			# Parse the condition
			cond = _parse_condition(t)
			if tt == _Type.OR:
				conds.append(cond)
			else:
				# tok is AND
				n = len(conds)
				conds[n-1] = condition.and_condition(conds[n-1], cond)
		else:
			raise _syntax_error(tok)

def _parse_condition(t):
	"""
	Parses the next condition.
	
	Args:
		t (_Tokeniser): the underlying tokeniser

	Raises:
		ParseError: 
			a syntax error occurred
	    ScanError:
    	    an invalid character was encountered
			
	"""
	if not isinstance(t, _Tokeniser):
		raise TypeError('expected a _Tokeniser')
	# Read the next token
	tok = next(t)
	# Switch on the token type
	tt = tok.type()
	if tt == _Type.EOF:
		t.push(tok)
		raise ParseError('unexpected EOF', tok)
	elif tt == _Type.OPENBRACKET:
		# Parse the contents of the brackets
		cond = _where_loop(t)
		# The next token needs to be a close bracket
		tok = next(t)
		if tok.type() != _Type.CLOSEBRACKET:
			raise ParseError("expected a close bracket ')'", tok)
		# Return the bracketed condition
		return cond
	elif tt == _Type.TRUE:
		return condition.TRUE
	elif tt == _Type.FALSE:
		return condition.FALSE
	elif tt == _Type.STRING:
		t.push(tok)
		return _parse_leaf(t)
	elif tt == _Type.NOT:
		# Parse what comes after the NOT
		cond = _parse_condition(t)
		return cond.negate()
	else:
		raise _syntax_error(tok)

def _comma_separated_tokens(t):
	"""
	Reads tokens of the form:
	
	'(' 'tok1' ',' 'tok2' ',' ... ',' 'tokN' ')'

	and returns ['tok1',...,'tokN']. If any of the 'toki' are not values that 
	can occur in a keyvalue record then a ParseError is raised.
	
	Args:
		t (_Tokeniser): the underlying tokeniser

	Raises:
		ParseError: 
			a syntax error occurred
	    ScanError:
    	    an invalid character was encountered
			
	"""
	if not isinstance(t, _Tokeniser):
		raise TypeError('expected a _Tokeniser')
	# Read the first token
	tok = next(t)
	if tok.type() != _Type.OPENBRACKET:
		raise ParseError("expected an open bracket '('", tok)
	# T holds the tokens
	T = []
	# Read the next token
	tok = next(t)
	# Are we done?
	if tok.type() == _Type.CLOSEBRACKET:
		return T
	# Loop over the tokens
	while True:
		if not tok.is_value():
			raise ParseError("expected value", tok)
		T.append(tok)
		# The next token must be a comma or close bracket
		tok = next(t)
		if tok.type() == _Type.CLOSEBRACKET:
			return T
		elif tok.type() != _Type.COMMA:
			raise ParseError("expected comma", tok)
		# Read in the next token
		tok = next(t)

def _value_and_value(t):
	"""
	Parses "val1 AND val2". Raises a ParseError unless val1 and val2
	are both values that can occur in a keyvalue record.
	
	Args:
		t (_Tokeniser): the underlying tokeniser

	Returns:
		val1, val2: the token values

	Raises:
		ParseError: 
			a syntax error occurred
	    ScanError:
    	    an invalid character was encountered
			
	"""
	if not isinstance(t, _Tokeniser):
		raise TypeError('expected a _Tokeniser')
	# Read the first value
	tok = next(t)
	if not tok.is_value():
		raise ParseError("expected value", tok)
	val1 = tok.value()
	# The next token should be "AND"
	tok = next(t)
	if tok.type() != _Type.AND:
		raise ParseError("expected AND", tok)
	# Read the second value
	tok = next(t)
	if not tok.is_value():
		raise ParseError("expected value", tok)
	return val1, tok.value()

def _bool_not_bool(t):
	"""
	Parses "[NOT] TRUE|FALSE" and returns the simplified bool.

	Args:
		t (_Tokeniser): the underlying tokeniser

	Raises:
		ParseError: 
			a syntax error occurred
	    ScanError:
    	    an invalid character was encountered
			
	"""
	if not isinstance(t, _Tokeniser):
		raise TypeError('expected a _Tokeniser')
	# Read the first value
	tok = next(t)
	# Switch on the type
	tt = tok.type()
	if tt == _Type.TRUE:
		return True
	elif tt == _Type.FALSE:
		return False
	elif tt == _Type.NOT:
		pass
	else:
		raise ParseError("expected boolean or NOT", tok)
	# If we're here then the token was a NOT. Read the next token.
	tok = next(t)
	tt = tok.type()
	# Switch on the type
	if tt == _Type.TRUE:
		return False # We negate the boolean
	elif tt == _Type.FALSE:
		return True # We negate the boolean
	else:
		raise ParseError("expected boolean", tok)

def _tokens_to_values(T):
	"""
	Converts the slice T of tokens to a slice of values. 
	
	Does not check if those tokens have values.
	"""
	result = []
	for t in T:
		if not isinstance(t, _Token):
			raise TypeError("expected a Token")
		result.append(t.value())
	return result

def _parse_leaf(t):
	"""
	Parses and returns a leaf condition.
	
	Assumes that the next token is a string.

	Args:
		t (_Tokeniser): the underlying tokeniser

	Raises:
		ParseError: 
			a syntax error occurred
	    ScanError:
    	    an invalid character was encountered
			
	"""
	if not isinstance(t, _Tokeniser):
		raise TypeError('expected a _Tokeniser')
	# Read the first value
	tok = next(t)
	if tok.type() != _Type.STRING:
		raise ParseError("expected a string", tok)
	lhs = tok.value()
	# Read the operator
	op = next(t)
	# Switch on the type
	opt = op.type()
	if (
		opt == _Type.EQ or
		opt == _Type.LT or
		opt == _Type.GT or
		opt == _Type.LE or
		opt == _Type.GE or
		opt == _Type.NE
	):
		# Read in the RHS
		rhs = next(t)
		if not rhs.is_value():
			raise ParseError("expected value", rhs)
		# Return the condition
		if opt == _Type.EQ:
			return condition.equal(lhs, rhs.value())
		elif opt == _Type.LT:
			return condition.less_than(lhs, rhs.value())
		elif opt == _Type.GT:
			return condition.greater_than(lhs, rhs.value())
		elif opt == _Type.LE:
			return condition.less_than_or_equal_to(lhs, rhs.value())
		elif opt == _Type.GE:
			return condition.greater_than_or_equal_to(lhs, rhs.value())
		elif opt == _Type.NE:
			return condition.not_equal(lhs, rhs.value())
		else:
			raise ParseError("expected operator", op)
	elif opt == _Type.IS:
		# Read in the RHS
		val = _bool_not_bool(t)
		return condition.is_condition(lhs, val)
	elif opt == _Type.IN:
		# Read in the values
		T = _comma_separated_tokens(t)
		return condition.in_condition(lhs, *_tokens_to_values(T))
	elif opt == _Type.BETWEEN:
		# Read in the values
		val1, val2 = _value_and_value(t)
		return condition.between(lhs, val1, val2)
	elif opt == _Type.NOT:
		# Read the next token
		op = next(t)
		# Switch on the type
		opt = op.type()
		if opt == _Type.IN:
			# Read in the values
			T = _comma_separated_tokens(t)
			return condition.not_in(lhs, *_tokens_to_values(T))
		elif opt == _Type.BETWEEN:
			# Read in the values
			val1, val2 = _value_and_value(t)
			return condition.not_between(lhs, val1, val2)
		else:
			raise _syntax_error(op)
	else:
		raise _syntax_error(op)
	
def _sort_loop(t):
	"""
	Parses a stream of tokens into an ORDER BY sort order.

	Args:
		t (_Tokeniser): 
			the underlying tokeniser

	Returns:
		order (List[sort.Order]): 
			the sort order

	Raises:
		ParseError: 
			a syntax error occurred
	    ScanError:
    	    an invalid character was encountered
			
	"""
	if not isinstance(t, _Tokeniser):
		raise TypeError('expected a _Tokeniser')
	# orders holds the sort orders
	orders = []
	# Start parsing the tokens
	while True:
		# Read the next token
		tok = next(t)
		# Switch on the token type
		tt = tok.type()
		if tt == _Type.LIMIT or tt == _Type.EOF:
			if len(orders) != 0:
				raise _syntax_error(tok)
			t.push(tok)
			return orders
		elif tt == _Type.STRING:
			pass
		else:
			raise _syntax_error(tok)
		# Note the key
		key = tok.value()
		# The next token should be a comma or the sort direction
		tok = next(t)
		tt = tok.type()
		if tt == _Type.ASC or tt == _Type.DESC:
			# Add the sort order
			if tt == _Type.ASC:
				orders.append(sort.ascending(key))
			else:
				orders.append(sort.descending(key))
			# We need to consider the next token
			tok = next(t)
			# Switch on the token type
			tt = tok.type()
			if tt == _Type.COMMA:
				pass
			elif tt == _Type.LIMIT or tt == _Type.EOF:
				t.push(tok)
				return orders
			else:
				raise _syntax_error(tok)
		elif tt == _Type.COMMA:
			# Add the sort order
			orders.append(sort.ascending(key))
		elif tt == _Type.LIMIT or tt == _Type.EOF:
			# Add the sort order
			orders.append(sort.ascending(key))
			t.push(tok)
			return orders
		else:
			raise _syntax_error(tok)
		
def _limit_loop(t):
	"""
	Parses a stream of tokens into an LIMIT value, or None if no limit is found.

	Args:
		t (_Tokeniser): 
			the underlying tokeniser

	Returns:
		limit (int or None): 
			the limit

	Raises:
		ParseError: 
			if the limit will not fit in a 64-bit integer, or a syntax error
			occurred
	    ScanError:
    	    an invalid character was encountered

	"""
	if not isinstance(t, _Tokeniser):
		raise TypeError('expected a _Tokeniser')
	# Read the next token
	tok = next(t)
	# Switch on the token type
	tt = tok.type()
	if tt == _Type.EOF:
		t.push(tok)
		return None
	elif tt == _Type.INT64:
		n = tok.value()
		if not 0 <= n <= _INT64_MAX:
			raise ParseError("limit out of range", tok)
		return n
	elif tt == _Type.UINT64:
		n = tok.value()
		if n > _INT64_MAX:
			raise ParseError("limit out of range", tok)
		return n
	else:
		raise _syntax_error(tok)

def _syntax_error(tok):
    """Returns a ParseError that represents a syntax error for the given Token."""
    return ParseError("syntax error", tok)

def _condition_from_tokens(t):
	"""
	Parses a stream of tokens into a condition.Condition.

	Args:
		t (_Tokeniser): the underlying tokeniser

	Raises:
		ParseError: 
			a syntax error occurred
	    ScanError:
    	    an invalid character was encountered
			
	"""
	if not isinstance(t, _Tokeniser):
		raise TypeError('expected a _Tokeniser')
	# Check for EOF
	tok = next(t)
	if tok.type() == _Type.EOF:
		return condition.TRUE
	# We allow for WHERE clauses to begin without a WHERE
	if tok.type() != _Type.WHERE:
		t.push(tok)
	# Parse the WHERE condition
	cond = _where_loop(t)
	# This should be the end of the stream
	tok = next(t)
	if tok.type() != _Type.EOF:
		raise _syntax_error(tok)
	# Return the condition
	return cond
	
def _order_from_tokens(t):
	"""
	Parses a stream of tokens into a sort order.

	Args:
		t (_Tokeniser): the underlying tokeniser

	Returns:
		a list of sort.Orders or None

	Raises:
		ParseError: 
			a syntax error occurred
	    ScanError:
    	    an invalid character was encountered
			
	"""
	if not isinstance(t, _Tokeniser):
		raise TypeError('expected a _Tokeniser')
	# Check for EOF
	tok = next(t)
	if tok.type() == _Type.EOF:
		return None
	# We allow for ORDER BY clauses to begin without an ORDER BY
	if tok.type() == _Type.ORDER:
		tok = next(t)
		if tok.type() != _Type.BY:
			raise _syntax_error(tok)
	else:
		t.push(tok)
	# Parse the ORDER BY condition
	order = _sort_loop(t)
	# This should be the end of the stream
	tok = next(t)
	if tok.type() != _Type.EOF:
		raise _syntax_error(tok)
	# Return the sort order
	return order

def _query_from_tokens(t):
	"""
	Parses a stream of tokens into a Query.

	Args:
		t (_Tokeniser): the underlying tokeniser

	Raises:
		ParseError: 
			a syntax error occurred
	    ScanError:
    	    an invalid character was encountered
			
	"""
	if not isinstance(t, _Tokeniser):
		raise TypeError('expected a _Tokeniser')
	# Initialise variables
	q = _new_query()
	has_where = False
	# Start parsing the tokens
	while True:
		# Read the next token
		tok = next(t)
		# Switch on the type
		tt = tok.type()
		if tt == _Type.EOF:
			return q
		elif tt == _Type.ORDER:
			# Check and update our state
			if not q.order is None:
				raise _syntax_error(tok)
			has_where = True
			# The next token must be BY
			tok = next(t)
			if tok.type() != _Type.BY:
				raise _syntax_error(tok)
			# Parse the ORDER BY sort order
			order = _sort_loop(t)
			if len(order) == 0:
				raise _syntax_error(tok)
			q.order = order
		elif tt == _Type.LIMIT:
			# Check and update our state
			if not q.limit is None:
				raise _syntax_error(tok)
			has_where = True
			# Parse the LIMIT
			n = _limit_loop(t)
			if n is None:
				raise _syntax_error(tok)
			q.limit = n
		else:
			# Check and update our state
			if has_where:
				raise _syntax_error(tok)
			has_where = True
			# We allow for WHERE clauses to begin without a WHERE
			if tt != _Type.WHERE:
				t.push(tok)
			# Parse the WHERE condition
			q.condition = _where_loop(t)

################################################################################
# Public functions
################################################################################

def parse_condition(s):
	"""
	Parses the SQL-formatted string s into a condition.Condition.
	
	Raises:
		ParseError: 
			a syntax error occurred
	    ScanError:
    	    an invalid character was encountered
			
	"""
	return _condition_from_tokens(_Tokeniser(_Scanner(s)))

def parse_order(s):
	"""
	Parses the SQL-formatted string s into a sort order, as a list of sort.Orders
	or None.

	Raises:
		ParseError: 
			a syntax error occurred
	    ScanError:
    	    an invalid character was encountered
			
	"""
	return _order_from_tokens(_Tokeniser(_Scanner(s)))

def parse_query(s):
	"""
	Parses the SQL-formatted string s into a Query.
	
	Raises:
		ParseError: 
			a syntax error occurred
	    ScanError:
    	    an invalid character was encountered
	
	"""
	return _query_from_tokens(_Tokeniser(_Scanner(s)))
