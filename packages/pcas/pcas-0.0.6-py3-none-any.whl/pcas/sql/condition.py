"""
Defines objects that represent logical conditions in a "where" clause.

"""

# To the extent possible under law, the author(s) have dedicated all copyright and
# related and neighboring rights to this software to the public domain worldwide.
# This software is distributed without any warranty.
#     
# You should have received a copy of the CC0 Public Domain Dedication along with
# this software. If not, see <http://creativecommons.org/publicdomain/zero/1.0/>.

import abc
import copy
from .exceptions import InvalidConditionError
from pcas.keyvalue import record

__all__ = [
    "Condition",
    "LeafOp",
    "Bool",
    "TRUE",
    "FALSE",
    "AndOp",
    "BetweenOp",
    "EqualOp",
    "GreaterThanOp",
    "GreaterThanOrEqualToOp",
    "InOp",
    "IsOp",
    "LessThanOp",
    "LessThanOrEqualToOp",
    "NotBetweenOp",
    "NotEqualOp",
    "NotInOp",
    "OrOp",
    "and_condition",
    "between",
    "equal",
    "greater_than",
    "greater_than_or_equal_to",
    "in_condition",
    "is_condition",
    "is_false",
    "is_true",
    "less_than",
    "less_than_or_equal_to",
    "not_in",
    "not_between",
    "not_equal",
    "or_condition",
    "condition_from_record",
]

class Condition(metaclass=abc.ABCMeta):
    """Defines the interface representing a condition."""

    def __init__(self):
        pass
    
    @abc.abstractmethod
    def __eq__(self, other):
        """
        Returns true if and only if this condition is equal to other.
        
        This tests equality; it does not check for equivalence.
        """
        return False

    @abc.abstractmethod
    def validate(self):
        """
        Raises an InvalidConditionError if this condition fails to validate.
        
        Returns:
            None
        
        """
    
    @abc.abstractmethod
    def negate(self):
        """Returns the negation of this condition."""

    @abc.abstractmethod
    def simplify(self):
        """
        Re-expresses this condition in terms of Bool, LeafOp, 
        AndOp, and OrOp conditions only.
        """

class LeafOp(Condition):
    """
    Describes a condition of the form "lhs op rhs" where lhs is a key and rhs is
    a value.
    
    """
    def __init__(self, lhs, rhs):
        if not isinstance(lhs, str):
            raise TypeError("expected a string")
        self._lhs = lhs
        self._rhs = rhs

    def __eq__(self, other):
        if type(self) != type(other):
            return False
        return (
            self.lhs() == other.lhs() and
            self.rhs() == other.rhs()
        )

    def validate(self):
        if not record.is_key(self.lhs()):
            raise _malformed_key_exception(self.lhs())
        if not record.is_value(self.rhs()):
            raise _value_type_exception(self.rhs())
    
    def lhs(self):
        """The LHS of the operator."""
        return self._lhs
    
    def rhs(self):
        """The RHS of the operator."""
        return self._rhs

    def simplify(self):
        return self
    

################################################################################
# Local functions
################################################################################

def _quote_key(s):
    """Returns a quoted form for the string s as a key."""
    s = s.replace('\\', '\\\\')
    s = s.replace("'", "\\'")
    return '\'' + s + '\''

def _quote_value(s):
    """Returns a quoted form for the string s as a value."""
    s = s.replace('\\', '\\\\')
    s = s.replace('"', '\\"')
    s = s.replace('\n', '\\n')
    s = s.replace('\r', '\\r')
    s = s.replace('\t', '\\t')
    return '"' + s + '"'

def _malformed_key_exception(k):
    """Returns an InvalidConditionError for the malformed key k."""
    return InvalidConditionError('malformed key: {}'.format(k))

def _value_type_exception(v):
    """Returns an InvalidConditionError for the value v with unsupported type."""
    return InvalidConditionError('unsupported value type: {}'.format(type(v)))
    
def _are_values_equal(vals1, vals2):
    """Returns true if and only if iterables vals1 and vals2 are equal."""
    if len(vals1) != len(vals2):
        return False
    for v1, v2 in zip(vals1, vals2):
        if v1 != v2:
            return False
    return True

def _format_value(v):
    """
    Returns a string representation of v, suitable for printing in an operator
    description.
    """
    if isinstance(v, bool):
        if v:
            return "TRUE"
        else:
            return "FALSE"
    if isinstance(v, str):
        return _quote_value(v)
    if isinstance(v, bytes):
        return str([str(x) for x in v])
    return str(v)

################################################################################
# Boolean conditions
################################################################################

class Bool(Condition):
    """Defines a truth valuation."""

    def __init__(self, value):
        if not isinstance(value, bool):
            raise TypeError("expected a boolean")
        self._value = value
    
    def __str__(self):
        if self._value:
            return "TRUE"
        return "FALSE"

    def __eq__(self, other):
        if not isinstance(other, Bool):
            return False
        return self._value == other._value

    def validate(self):
        pass
    
    def negate(self):
        if self._value:
            return FALSE
        return TRUE
    
    def simplify(self):
        return self

    def value(self):
        return self._value


TRUE = Bool(True)
FALSE = Bool(False)

################################################################################
# IS conditions
################################################################################

class IsOp(Condition):
    """Describes an IS condition."""

    def __init__(self, key, value):
        """
        Creates the IS condition 'key IS value'.
        
        Args:
            key (str): the key
            value (bool): the value

        """
        # Sanity checks
        if not isinstance(key, str):
            raise TypeError("expected a string")
        if not isinstance(value, bool):
            raise TypeError("expected a boolean value")
        self._key = key
        self._value = value

    def __str__(self):
        valString = "FALSE"
        if self._value:
            valString = "TRUE"
        return _quote_key(self.lhs()) + " IS " + valString

    def __eq__(self, other):
        if not isinstance(other, IsOp):
            return False
        return self.lhs() == other.lhs() and self.value() == other.value()  

    def lhs(self):
        """Returns the LHS of the operator."""
        return self._key
    
    def value(self):
        """Returns the RHS of the operator."""
        return self._value

    def negate(self):
        return in_condition(self.lhs(), not self.value())
    
    def simplify(self):
        return equal(self.lhs(), self.value())
    
    def validate(self):
        if not record.is_key(self.lhs()):
            raise _malformed_key_exception(self.lhs())      


def is_condition(lhs, rhs):
    """Returns the operator 'lhs IS rhs' as an IsOp."""
    return IsOp(lhs, rhs)

def is_true(lhs):
    """Returns the operator 'lhs IS TRUE' as an IsOp."""
    return IsOp(lhs, True)

def is_false(lhs):
    """Returns the operator 'lhs IS FALSE' as an IsOp."""
    return IsOp(lhs, False)

################################################################################
# IN conditions
################################################################################

class InOp(Condition):
    """Describes an IN condition."""

    def __init__(self, lhs, *values):
        """
        Returns a new IN operator. 

        Args:
            lhs (str): the LHS of the IN condition
            values: the values to match against, which must be of types that can
                        occur in a keyvalue record.

        If no values are provided then this is equivalent to the False valuation.

        """
        if not isinstance(lhs, str):
            raise TypeError('lhs should be a string')
        self._lhs = lhs
        self._values = copy.deepcopy(values)

    def __str__(self):
        valStrings = [_quote_value(x) for x in self._values]
        return _quote_key(self.lhs()) + ' IN (' + ", ".join(valStrings) + ')'

    def __eq__(self, other):
        if not isinstance(other, InOp):
            return False
        if self.lhs() != other.lhs():
            return False
        return _are_values_equal(self.values(), other.values())

    def validate(self):
        if not record.is_key(self.lhs()):
            raise _malformed_key_exception(self.lhs())
        for x in self._values:
            if not record.is_value(x):
                raise _value_type_exception(x)
    
    def lhs(self):
        """Returns the LHS of the operator."""
        return self._lhs

    def values(self):
        """Returns a list of values for the operator."""
        return copy.deepcopy(self._values)
    
    def negate(self):
        return not_in(self.lhs(), values=self.values())
    
    def simplify(self):
        lhs = self.lhs()
        values = self.values()
        if len(values) == 0:
            return FALSE
        elif len(values) == 1:
            return equal(lhs, values[0])
        else:
            return or_condition(*[equal(lhs, rhs) for rhs in values])
        

def in_condition(lhs, *values):
    """
    Returns a new IN operator as an InOp or equivalent Condition. The IN operator
    can be used to match a value against a list of values and is equivalent to
    successive OR operators:
    
    lhs = values[0] OR lhs = values[1] OR ... OR lhs = values[len(values)-1]

    If no values are provided then this is equivalent to the False valuation.

    Args:
        lhs (str): the LHS of the IN condition
        values: the values to match against, which must be of types that can
                    occur in a keyvalue record.

    """
    return InOp(lhs, *values).simplify()

################################################################################
# NOT IN conditions
################################################################################

class NotInOp(Condition):
    """Describes an IN condition."""

    def __init__(self, lhs, *values):
        """
        Returns a new NOT IN operator. 

        Args:
            lhs (str): the LHS of the NOT IN condition
            values: the values to match against, which must be of types that can
                        occur in a keyvalue record.

        If no values are provided then this is equivalent to the True valuation.

        """
        if not isinstance(lhs, str):
            raise TypeError('lhs should be a string')
        self._lhs = lhs
        self._values = copy.deepcopy(values)

    def __str__(self):
        valStrings = [_quote_value(x) for x in self._values]
        return _quote_key(self.lhs()) + ' NOT IN (' + ", ".join(valStrings) + ')'

    def __eq__(self, other):
        if not isinstance(other, NotInOp):
            return False
        if self.lhs() != other.lhs():
            return False
        return _are_values_equal(self.values(), other.values())

    def validate(self):
        if not record.is_key(self.lhs()):
            raise _malformed_key_exception(self.lhs())
        for x in self._values:
            if not record.is_value(x):
                raise _value_type_exception(x)
    
    def lhs(self):
        """Returns the LHS of the operator."""
        return self._lhs

    def values(self):
        """Returns a list of values for the operator."""
        return copy.deepcopy(self._values)
    
    def negate(self):
        return in_condition(self.lhs(), values=self.values())
    
    def simplify(self):
        lhs = self.lhs()
        values = self.values()
        if len(values) == 0:
            return FALSE
        elif len(values) == 1:
            return not_equal(lhs, values[0])
        else:
            return and_condition(*[not_equal(lhs, rhs) for rhs in values])
        

def not_in(lhs, *values):
    """
    Returns a new NOT IN operator as a NotInOp or equivalent Condition. The 
    NOT IN operator can be used to match a value against a list of values and 
    is equivalent to successive AND operators:
    
    lhs != values[0] AND ... AND lhs != values[len(values)-1]

    If no values are provided then this is equivalent to the True valuation.

    Args:
        lhs (str): the LHS of the NOT IN condition
        values: the values to match against, which must be of types that can
                    occur in a keyvalue record.

    """
    return NotInOp(lhs, *values).simplify()

################################################################################
# BETWEEN conditions
################################################################################

class BetweenOp(Condition):
    """Describes a BETWEEN condition."""

    def __init__(self, lhs, lower, upper):
        """
        Returns a new BETWEEN operator. 

        Args:
            lhs (str): the LHS of the IN condition
            lower, upper: the upper and lower values in the range, which must be
                            of types that can occur in a keyvalue record.

        """
        if not isinstance(lhs, str):
            raise TypeError('lhs should be a string')
        self._lhs = lhs
        self._lower = lower
        self._upper = upper

    def __str__(self):
        return '{} BETWEEN {} AND {}'.format(_quote_key(self.lhs()), _format_value(self.lower()), _format_value(self.upper()))

    def __eq__(self, other):
        if not isinstance(other, BetweenOp):
            return False
        return (
            self.lhs() == other.lhs() and
            self.lower() == other.lower() and
            self.upper() == other.upper()
        )

    def validate(self):
        if not record.is_key(self.lhs()):
            raise _malformed_key_exception(self.lhs())
        for x in [self.lower(), self.upper()]:
            if not record.is_value(x):
                raise _value_type_exception(x)
            if isinstance(x, bool) or isinstance(x, Bool):
                raise InvalidConditionError("BETWEEN operator not supported for Boolean value type")
    
    def lhs(self):
        """Returns the LHS of the operator."""
        return self._lhs

    def lower(self):
        """Returns the lower value for the operator."""
        return self._lower

    def upper(self):
        """Returns the upper value for the operator."""
        return self._upper  
        
    def negate(self):
        return not_between(self.lhs(), self.lower(), self.upper())
    
    def simplify(self):
        lhs = self.lhs()
        return and_condition(
            greater_than_or_equal_to(lhs, self.lower()),
            less_than_or_equal_to(lhs, self.upper())
        )        


def between(lhs, lower, upper):
    """
    Returns a new BETWEEN operator as a BetweenOp or equivalent Condition. The
    BETWEEN operator can be used to match against a range of values and is
    equivalent to:

    lhs >= lower AND lhs <= upper.

    Args:
        lhs (str): the LHS of the BETWEEN condition
        lower, upper: the upper and lower values in the range, which must be
                        of types that can occur in a keyvalue record.

    """
    return BetweenOp(lhs, lower, upper)

################################################################################
# NOT BETWEEN conditions
################################################################################


class NotBetweenOp(Condition):
    """Describes a NOT BETWEEN condition."""

    def __init__(self, lhs, lower, upper):
        """
        Returns a new NOT BETWEEN operator. 

        Args:
            lhs (str): the LHS of the IN condition
            lower, upper: the upper and lower values in the range, which must be
                            of types that can occur in a keyvalue record.

        """
        if not isinstance(lhs, str):
            raise TypeError('lhs should be a string')
        self._lhs = lhs
        self._lower = lower
        self._upper = upper

    def __str__(self):
        return '{} NOT BETWEEN {} AND {}'.format(_quote_key(self.lhs()), _format_value(self.lower()), _format_value(self.upper()))

    def __eq__(self, other):
        if not isinstance(other, NotBetweenOp):
            return False
        return (
            self.lhs() == other.lhs() and
            self.lower() == other.lower() and
            self.upper() == other.upper()
        )

    def validate(self):
        if not record.is_key(self.lhs()):
            raise _malformed_key_exception(self.lhs())
        for x in [self.lower(), self.upper()]:
            if not record.is_value(x):
                raise _value_type_exception(x)
            if isinstance(x, bool) or isinstance(x, Bool):
                raise InvalidConditionError("NOT BETWEEN operator not supported for Boolean value type")
    
    def lhs(self):
        """Returns the LHS of the operator."""
        return self._lhs

    def lower(self):
        """Returns the lower value for the operator."""
        return self._lower

    def upper(self):
        """Returns the upper value for the operator."""
        return self._upper  
        
    def negate(self):
        return between(self.lhs(), self.lower(), self.upper())
    
    def simplify(self):
        lhs = self.lhs()
        return or_condition(
            less_than(lhs, self.lower()),
            greater_than(lhs, self.upper())
        )        


def not_between(lhs, lower, upper):
    """
    Returns a new NOT BETWEEN operator as a NotBetweenOp or equivalent Condition. 
    The NOT BETWEEN operator can be used to match against a range of values and is
    equivalent to:

    lhs < lower OR lhs > upper.

    Args:
        lhs (str): the LHS of the NOT BETWEEN condition
        lower, upper: the upper and lower values in the range, which must be
                        of types that can occur in a keyvalue record.

    """
    return NotBetweenOp(lhs, lower, upper)

################################################################################
# Equality conditions
################################################################################

class EqualOp(LeafOp):
    """Represents an equality condition."""

    def __init__(self, lhs, rhs):
        super().__init__(lhs, rhs)

    def __str__(self):
        return '{} = {}'.format(self.lhs(), self.rhs())
    
    def negate(self):
        return not_equal(self.lhs(), self.rhs())
    
def equal(lhs, rhs):
    """Returns the operator "lhs = rhs" as an EqualOp."""
    return EqualOp(lhs ,rhs)

class NotEqualOp(LeafOp):
    """Represents a negated equality condition."""

    def __init__(self, lhs, rhs):
        super().__init__(lhs, rhs)

    def __str__(self):
        return '{} != {}'.format(self.lhs(), self.rhs())
    
    def negate(self):
        return equal(self.lhs(), self.rhs())
    
def not_equal(lhs, rhs):
    """Returns the operator "lhs != rhs" as a NotEqualOp."""
    return NotEqualOp(lhs ,rhs)

################################################################################
# Inequality conditions
################################################################################

class GreaterThanOp(LeafOp):
    """Represents a greater than condition."""

    def __init__(self, lhs, rhs):
        super().__init__(lhs, rhs)

    def __str__(self):
        return '{} > {}'.format(self.lhs(), self.rhs())
    
    def negate(self):
        return less_than_or_equal_to(self.lhs(), self.rhs())
    
def greater_than(lhs, rhs):
    """Returns the operator "lhs > rhs" as a GreaterThanOp."""
    return GreaterThanOp(lhs ,rhs)

class GreaterThanOrEqualToOp(LeafOp):
    """Represents a greater than or equal to condition."""

    def __init__(self, lhs, rhs):
        super().__init__(lhs, rhs)

    def __str__(self):
        return '{} >= {}'.format(self.lhs(), self.rhs())
    
    def negate(self):
        return less_than(self.lhs(), self.rhs())
    
def greater_than_or_equal_to(lhs, rhs):
    """Returns the operator "lhs >= rhs" as a GreaterThanOrEqualToOp."""
    return GreaterThanOrEqualToOp(lhs ,rhs)

class LessThanOp(LeafOp):
    """Represents a less than condition."""

    def __init__(self, lhs, rhs):
        super().__init__(lhs, rhs)

    def __str__(self):
        return '{} < {}'.format(self.lhs(), self.rhs())
    
    def negate(self):
        return greater_than_or_equal_to(self.lhs(), self.rhs())
    
def less_than(lhs, rhs):
    """Returns the operator "lhs < rhs" as a LessThanOp."""
    return LessThanOp(lhs ,rhs)

class LessThanOrEqualToOp(LeafOp):
    """Represents a less than or equal to condition."""

    def __init__(self, lhs, rhs):
        super().__init__(lhs, rhs)

    def __str__(self):
        return '{} <= {}'.format(self.lhs(), self.rhs())
    
    def negate(self):
        return greater_than(self.lhs(), self.rhs())
    
def less_than_or_equal_to(lhs, rhs):
    """Returns the operator "lhs <= rhs" as a LessThanOrEqualToOp."""
    return LessThanOrEqualToOp(lhs ,rhs)

################################################################################
# AND conditions
################################################################################

def _flatten_and(conds):
    """
    Expands any AND operators appearing in the given Conditions, returning the
    flattened conditions.
    """
    new_conds = []
    for c in conds:
        if not isinstance(c, Condition):
            raise TypeError("expected a Condition")
        elif isinstance(c, AndOp):
            new_conds.extend(c.conditions())
        elif isinstance(c, Bool):
            if not c.value():
                return [FALSE]
        elif isinstance(c, bool):
            if not c:
                return [FALSE]
        else:
            new_conds.append(c)
    return new_conds

class AndOp(Condition):
    """Describes an AND operator."""

    def __init__(self, *conditions):
        self._conditions = copy.deepcopy(conditions)
    
    def __str__(self):
        S = [str(c) for c in self.conditions()]
        return '(' + " AND ".join(S) + ')'

    def __eq__(self, other):
        if not isinstance(other, AndOp):
            return False
        conds1 = self.conditions()
        conds2 = other.conditions()
        if len(conds1) != len(conds2):
            return False
        for c1, c2 in zip(conds1, conds2):
            if c1 != c2:
                return False
        return True

    def validate(self):
        if len(self.conditions()) < 2:
            raise InvalidConditionError("an AND operator requires two or more conditions")
        for c in self.conditions():
            c.validate()
    
    def negate(self):
        return or_condition(conditions=[c.negate() for c in self.conditions()])
    
    def conditions(self):
        """Conditions returns the conditions that form the AND operator."""
        return copy.deepcopy(self._conditions)
    
    def simplify(self):
        return and_condition([c.simplify() for c in self.conditions()])

    
def and_condition(*conditions):
    """
    Returns a new AND operator as an AndOp or equivalent Condition. That is,
    returns a Condition equivalent to:
    
    cond1 AND cond2 AND ... AND condN.
    
    If no conditions are provided then this equivalent to the True valuation.

    """
    conds = _flatten_and(conditions)
    if len(conds) == 0:
        return TRUE
    elif len(conds) == 1:
        return conds[0]
    return AndOp(*conds)

################################################################################
# OR conditions
################################################################################

def _flatten_or(conds):
    """
    Expands any OR operators appearing in the given Conditions, returning the
    flattened conditions.
    """
    new_conds = []
    for c in conds:
        if not isinstance(c, Condition):
            raise TypeError("expected a Condition")
        elif isinstance(c, OrOp):
            new_conds.extend(c.conditions())
        elif isinstance(c, Bool):
            if c.value():
                return [TRUE]
        elif isinstance(c, bool):
            if c:
                return [TRUE]
        else:
            new_conds.append(c)
    return new_conds

class OrOp(Condition):
    """Describes an OR operator."""

    def __init__(self, *conditions):
        self._conditions = copy.deepcopy(conditions)
    
    def __str__(self):
        S = [str(c) for c in self.conditions()]
        return '(' + " OR ".join(S) + ')'

    def __eq__(self, other):
        if not isinstance(other, OrOp):
            return False
        conds1 = self.conditions()
        conds2 = other.conditions()
        if len(conds1) != len(conds2):
            return False
        for c1, c2 in zip(conds1, conds2):
            if c1 != c2:
                return False
        return True

    def validate(self):
        if len(self.conditions()) < 2:
            raise InvalidConditionError("an OR operator requires two or more conditions")
        for c in self.conditions():
            c.validate()
    
    def negate(self):
        return and_condition(conditions=[c.negate() for c in self.conditions()])
    
    def conditions(self):
        """Conditions returns the conditions that form the OR operator."""
        return copy.deepcopy(self._conditions)
    
    def simplify(self):
        return or_condition([c.simplify() for c in self.conditions()])

    
def or_condition(*conditions):
    """
    Returns a new Or operator as an OrOp or equivalent Condition. That is,
    returns a Condition equivalent to:
    
    cond1 OR cond2 OR ... OR condN.
    
    If no conditions are provided then this equivalent to the False valuation.

    """
    conds = _flatten_or(conditions)
    if len(conds) == 0:
        return FALSE
    elif len(conds) == 1:
        return conds[0]
    return OrOp(*conds)

################################################################################
# Conversion functions
################################################################################

def condition_from_record(d):
    """Converts the dictionary d to a Condition."""
    return and_condition(*[equal(k, v) for k, v in d.items()])

