"""
Provides functions to convert objects to and from their gRPC representation.

"""

# To the extent possible under law, the author(s) have dedicated all copyright and
# related and neighboring rights to this software to the public domain worldwide.
# This software is distributed without any warranty.
#     
# You should have received a copy of the CC0 Public Domain Dedication along with
# this software. If not, see <http://creativecommons.org/publicdomain/zero/1.0/>.

from ._kvdb_pb2 import (
    ConditionAndReplacement, 
    ConditionTemplateOrderAndLimit,
    NumberOfRecords, 
    Record,
    Index,
    Key,
    KeyList,
)
from ._value_pb2 import Value
from ._sort_pb2 import (
    Order,
    OrderBy,
    Direction,
)
from ._condition_pb2 import (
    Condition,
    LeafOperator, 
    LhsBool, 
    LhsLowerUpper, 
    LhsManyValues, 
    ManyConditions, 
)
from pcas import sql
from .exceptions import ServerError

_MAX_INT64 = 9223372036854775807
_MIN_INT64 = -9223372036854775808

def _examine_trailer_metadata(md):
    """
    Examines the gRPC trailing metadata md, and raises an appropriate ServerError if
    the 'error' tag is present.
    """
    # Convert the metadata to a dictionary
    d = {x.key: x.value for x in md}
    # If there is no error, we return immediately
    if not 'error' in d:
        return
    # Grab the error
    error = d['error']
    # Grab the error code
    if 'error_code' in d:
        code = int(d['error_code'])
    else:
        code = None
    # Grab the causes
    causes = []
    n = 1
    while True:
        k = "error_cause_{}".format(n)
        if k in d:
            causes.append(d[k])
            n += 1
        else:
            break
    if len(causes) == 0:
        causes = None
    # Grab the cause_codes
    cause_codes = []
    n = 1
    while True:
        k = "error_cause_{}_code".format(n)
        if k in d:
            cause_codes.append(int(d[k]))
            n += 1
        else:
            break
    if len(cause_codes) == 0:
        cause_codes = None
    # Create and raise the exception
    raise ServerError(error, code, causes, cause_codes)


def _to_value(x):
    """Convert a Python object to a value_pb2.Value.

    Args:
        x (Any): the object to be converted

    Returns:
        value_pb2.Value: The return value. 

    Raises:
        TypeError: 
            if the value is not of a type that can be represented
            in a pcas keyvalue record

    """
    # Special case to handle Sage integers
    if str(type(x)) == "<class 'sage.rings.integer.Integer'>":
        x = int(x)
    # Do the conversion
    if isinstance(x, bool):
        return Value(
            type = Value.Type.Value('BOOL'),
            bool_value = x,
        )
    elif isinstance(x, int):
        if x > _MAX_INT64 or x < _MIN_INT64:
            raise ValueError("integer overflow")
        return Value(
            type = Value.Type.Value('INT'),
            int64_value=x,
        )
    elif isinstance(x, float):
        return Value(
            type=Value.Type.Value('FLOAT64'),
            double_value=x,
        )
    elif isinstance(x, str):
        return Value(
            type=Value.Type.Value('STRING'),
            string_value=x,
        )
    elif isinstance(x,bytes):
        return Value(
            type=Value.Type.Value('BYTESLICE'),
            bytes_value=x,
        )
    raise TypeError("cannot convert data of this type to a Value")

def _from_value(v):
    """Convert a value_pb2.Value to the corresponding Python value.

    Args:
        v (value_pb2.Value): the value to be converted

    Returns:
        Any: The return value. 

    """
    # Sanity check
    if type(v) != Value:
        raise TypeError('expected a value_pb2.Value')
    # Convert the value
    if v.type == Value.Type.Value('UNDEFINED'):
        raise ValueError('illegal value')
    elif v.type == Value.Type.Value('INT'):
        return v.int64_value
    elif (v.type == Value.Type.Value('INT8') or
        v.type == Value.Type.Value('INT16') or
        v.type == Value.Type.Value('INT32')):
        return v.int32_value
    elif v.type == Value.Type.Value('INT64'):
        return v.int64_value
    elif v.type == Value.Type.Value('UINT'):
        return v.uint64_value
    elif (v.type == Value.Type.Value('UINT8') or
        v.type == Value.Type.Value('UINT16') or
        v.type == Value.Type.Value('UINT32')):
        return v.uint32_value
    elif v.type == Value.Type.Value('UINT64'):
        return v.uint64_value
    elif v.type == Value.Type.Value('BOOL'):
        return v.bool_value
    elif v.type == Value.Type.Value('FLOAT64'):
        return v.double_value
    elif v.type == Value.Type.Value('STRING'):
        return v.string_value
    elif v.type == Value.Type.Value('BYTESLICE'):
        return v.bytes_value
    else:
        raise ValueError('unexpected type')

def _to_record(d):
    """Convert a dictionary to a _kvdb_pb2.Record.

    Args:
        d (Dict[str, Any]): the dictionary to be converted

    Returns:
        _kvdb_pb2.Record: The return value. 

    Raises:
        TypeError: 
            if a value is encountered that is not of a type 
            that can be represented in a pcas keyvalue record

    """
    # Sanity checks
    if not isinstance(d,dict):
        raise TypeError('argument must be a dictionary')
    for k in d:
        if not isinstance(k, str):
            raise TypeError('the keys must be strings')
    # Convert the entries
    result = Record()
    for k, v in d.items():
            result.values[k].CopyFrom(_to_value(v))
    return result

def _from_record(rec):
    """Convert a _kvdb_pb2.Record to a dictionary.

    Args:
        rec (_kvdb_pb2.Record): the record to be converted

    Returns:
        Dict[str,Any]: The return value. 

    """
    # Sanity check
    if type(rec) != Record:
        raise TypeError('expected a _kvdb_pb2.Record')
    # Convert the values
    result = {}
    for k in rec.values:
        result[k] = _from_value(rec.values[k])
    return result

def _to_record_iterator(iter):
    """Convert an iterator of dictionaries to an iterator of
    objects of type _kvdb_pb2.Record.

    Args:
        iter (Iterable[Dict[str, Any]]): the iterator to be converted

    Returns:
        Iterable[_kvdb_pb2.Record]: The return value. 

    """
    return _RecordIterator(iter)

class _RecordIterator:
    """
    An iterator of objects of type _kvdb_pb2.Record that wraps an
    underlying iterator of dictionaries. The last exception raised,
    if any, is available via the method last_exception.

    Args:
        itr (Iterable[Dict[str, Any]]): the underlying iterator
        
    """
    def __init__(self, itr):
        # record the underlying record iterator
        self._itr = iter(itr)
        # record that we have not yet raised an exception
        self._last_e = None
    
    def __iter__(self):
        return self

    def __next__(self):
        try:
            return _to_record(next(self._itr))
        except Exception as e:
            self._last_e = e
            raise
    
    def last_exception(self):
        """The last exception, if any, encountered during iteration."""
        return self._last_e

def _to_leaf_op(c):
    """Converts a condition.LeafOp to a condition_pb2.LeafOperator."""
    # Convert the RHS
    rhs = _to_value(c.rhs())
    # Set the Opcode
    op = LeafOperator.LeafType.UNDEFINED
    if isinstance(c, sql.EqualOp):
        op = LeafOperator.LeafType.EQ
    elif isinstance(c, sql.NotEqualOp):
        op = LeafOperator.LeafType.NE
    elif isinstance(c, sql.LessThanOp):
        op = LeafOperator.LeafType.LT
    elif isinstance(c, sql.GreaterThanOp):
        op = LeafOperator.LeafType.GT
    elif isinstance(c, sql.LessThanOrEqualToOp):
        op = LeafOperator.LeafType.LE
    elif isinstance(c, sql.GreaterThanOrEqualToOp):
        op = LeafOperator.LeafType.GT
    # Create the return value
    result = LeafOperator()
    result.lhs = c.lhs()
    result.opcode = op
    result.rhs.CopyFrom(rhs)
    return result

def _to_lhs_bool(lhs, b):
    """Converts a string lhs and a bool b to a condition_pb2.LhsBool."""
    if not isinstance(lhs, str):
        raise TypeError("expected a string")
    if not isinstance(b, bool):
        raise TypeError("expected a boolean")
    result = LhsBool()
    result.lhs = lhs
    result.bool_value = b
    return result

def _to_lhs_values(lhs, values):
    """
    Converts a string and an iterable of values to a
    condition_pb2.LhsManyValues.
    
    Args:
        lhs (str): the string
        values (Iterable[Any]): the values
    
    Returns:
        condition_pb2.LhsManyValues

    """
    if not isinstance(lhs, str):
        raise TypeError("expected a string")
    # Convert the values
    vs = [_to_value(v) for v in values]
    # Create the return value
    result = LhsManyValues(value=vs)
    result.lhs = lhs
    return result

def _to_lhs_lower_upper(lhs, lower, upper):
    """
    Converts a string and lower and upper values to a
    condition_pb2.LhsLowerUpper.

    Args:
        lhs (str): the string
        lower (Any): the lower value
        upper (Any): the upper value

    """
    if not isinstance(lhs, str):
        raise TypeError("expected a string")
    # Convert the lower and upper values
    l = _to_value(lower)
    u = _to_value(upper)
    # Create the return value
    result = LhsLowerUpper()
    result.lhs = lhs
    result.lower.CopyFrom(l)
    result.upper.CopyFrom(u)
    return result

def _to_conditions(cs):
    """
    Converts an iterable of conditions to a condition_pb2.ManyConditions.
    
    Args:
        cs (Iterable[sql.condition.Condition]): the conditions

    Returns:
        condition_pb2.ManyConditions

    """
    # Convert the conditions
    conds = [_to_condition(c) for c in cs]
    # Wrap them up and return
    return ManyConditions(cond=conds)

def _to_condition(s):
    """
    Converts a condition to a condition_pb2.Condition.

    Args:
        s (Union[str, Dict[str, Any], pcas.sql.condition.Condition]): 
            the condition, as a string in SQL format or a key-value record
            or a Condition object from the sql package
        
    The SQL format for condition is documented in the sql package.

    Returns:
        condition_pb2.Condition

    """
    if isinstance(s, str):
        # Parse the string
        c = sql.parse_condition(s)
    elif isinstance(s, dict):
        # Convert the key-value record to a condition
        c = sql.condition_from_record(s)
    elif isinstance(s, sql.condition.Condition):
        c = s
    else:
        raise TypeError("expected a string or a keyvalue record or a pcas.sqp.condition.Condition object")
    # Validate the resulting condition
    c.validate()
    # We handle the different types of conditions separately
    result = Condition()
    if isinstance(c, sql.condition.Bool):
        # TRUE or FALSE
        result.type = Condition.CondType.BOOL
        result.bool_value = c.value()
    elif isinstance(c, sql.condition.LeafOp):
        # Leaf operators
        leaf = _to_leaf_op(c)
        result.type = Condition.CondType.LEAF
        result.leaf_value.CopyFrom(leaf)
    elif isinstance(c, sql.condition.InOp):
        # IN
        x = _to_lhs_values(c.lhs(), c.values())
        result.type = Condition.CondType.IN
        result.lhs_many_values_value.CopyFrom(x) 
    elif isinstance(c, sql.condition.NotInOp):
        # NOTIN
        x = _to_lhs_values(c.lhs(), c.values())
        result.type = Condition.CondType.NOTIN
        result.lhs_many_values_value.CopyFrom(x)
    elif isinstance(c, sql.condition.BetweenOp):
        # BETWEEN
        x = _to_lhs_lower_upper(c.lhs(), c.lower(), c.upper())
        result.type = Condition.CondType.BETWEEN
        result.lhs_lower_upper_value.CopyFrom(x)
    elif isinstance(c, sql.condition.NotBetweenOp):
        # NOT BETWEEN
        x = _to_lhs_lower_upper(c.lhs(), c.lower(), c.upper())
        result.type = Condition.CondType.NOTBETWEEN
        result.lhs_lower_upper_value.CopyFrom(x)
    elif isinstance(c, sql.condition.AndOp):
        # AND
        cs = _to_conditions(c.conditions())
        result.type = Condition.CondType.AND
        result.many_conditions_value.CopyFrom(cs)
    elif isinstance(c, sql.condition.OrOp):
        # OR
        cs = _to_conditions(c.conditions())
        result.type = Condition.CondType.OR
        result.many_conditions_value.CopyFrom(cs)
    elif isinstance(c, sql.condition.IsOp):
        # IS
        x = _to_lhs_bool(c.lhs(), c.value())
        result.type = Condition.CondType.IS
        result.lhs_bool_value.CopyFrom(x)
    else:
        raise ValueError("unknown condition")
    return result

def _from_number_of_records(nr):
    """Convert a _kvdb_pb2.NumberOfRecords nr to an int."""
    if not isinstance(nr, NumberOfRecords):
        raise TypeError("expected a NumberOfRecords")
    return nr.n

def _to_condition_and_replacement(condition, replacement):
    """
    Converts a dictionary and an SQL-formatted string to a 
    _kvdb_pb2.ConditionAndReplacement.

    Args:
        s (Union[str, Dict[str, Any]]): 
            the condition, as a string in SQL format or a key-value record
        replacement (Dict[Str, Any]):
            the replacement record
        
    The SQL format for condition is documented in the sql package.

    Returns:
        _kvdb_pb2.ConditionAndReplacement

    """
    result = ConditionAndReplacement()
    result.condition.CopyFrom(_to_condition(condition))
    result.replacement.CopyFrom(_to_record(replacement))
    return result

def _to_order_by(x):
    """
    Converts the given sort order to a _kvdb_pb2.OrderBy.

    Args:
        x (Union[None, pcas.sql.sort.Order, List[pcas.sql.sort.Order]]):
            the sort order
    
    Raises:
        ValueError:
            if x is an empty list

    """
    # Handle the trivial case
    if x is None:
        return OrderBy()
    # Convert a singleton to a length-one list
    if isinstance(x, sql.sort.Order):
        x = [x]
    # Handle the list case
    if not isinstance(x, list):
        raise TypeError("expected a list")
    elif len(x) == 0:
        raise ValueError("expected a non-empty list")
    # convert the elements of x
    converted_orders = []
    for y in x:
        if not isinstance(y, sql.sort.Order):
            raise TypeError("expected a pcas.sql.sort.Order")
        z = Order()
        z.key = y.key()
        if y.is_ascending():
            z.direction.CopyFrom(Direction(direction=False))
        else:
            z.direction.CopyFrom(Direction(direction=True))
        converted_orders.append(z)
    # package up the converted elements and return
    result = OrderBy()
    result.order.extend(converted_orders)
    return result

def _to_condition_template_order_and_limit(template, selector, order, limit):
    """
    Converts the given template, selector, order, and limit to a 
    _kvdb_pb2.ConditionTemplateOrderAndLimit.

    Args:
        template (Dict[str, Any]):
            the format in which to return the data
        selector (Union[str, Dict[str, Any]]): 
            the condition to match, as a string in SQL format or a key-value record
        order (Union[pcas.sql.sort.Order, List[pcas.sql.sort.Order], None]):
            the order in which to sort records
        limit (Union[int, None]):
            the maximum number of records to return
        
    The SQL format for condition is documented in the sql package.

    Returns:
        _kvdb_pb2.ConditionTemplateOrderAndLimit

    Raises:
        pcas.sql.exceptions.InvalidConditionError: 
            if the condition is invalid
        pcas.sql.exceptions.ParseError: 
            if the condition fails to parse
        pcas.sql.exceptions.ScanError:  
            if the condition fails to parse
        TypeError:  
            if record conversion is not possible
        ValueError: 
            if an illegal value is encountered

    """
    result = ConditionTemplateOrderAndLimit()
    # parse the condition
    q = sql.parse_query(selector)
    # check that the limit wasn't provided twice
    if (not q.limit is None) and (not limit is None):
        raise ValueError("limit provided explicitly and also in the selector")
    # check that the order wasn't provided twice
    if (not q.order is None) and (not order is None):
        raise ValueError("order provided explicitly and also in the selector")
    # process the limit
    if q.limit is None:
        if limit is None:
            q.limit = -1
        elif not isinstance(limit, int):
            raise TypeError("the limit must be an integer")
        elif limit <= 0:
            raise ValueError("the limit must be positive")
        else:
            # record the limit
            q.limit = limit
    # process the order
    if q.order is None:
        if not order is None:
            # Promote singletons to singleton lists
            if isinstance(order, sql.sort.Order):
                order = [order]
            if not isinstance(order, list):
                raise TypeError("the limit must be a pcas.sql.sort.Order or a list of pcas.sql.sort.Orders")
            for x in order:
                if not isinstance(x, sql.sort.Order):
                    raise TypeError("expected a pcas.sql.sort.Order")
                x.validate()
            # record the order
            q.order = order
    # construct the return value
    result.condition.CopyFrom(_to_condition(q.condition))
    result.template.CopyFrom(_to_record(template))
    result.order.CopyFrom(_to_order_by(q.order))
    result.limit = q.limit
    return result

def _from_record_iterator(itr):
    """
    Wraps an iterable of _kvdb_pb2.Records as an iterator of key-value records.
    
    Args:
        itr (Iterable[_kvdb_pb2.Record]):
            the underlying iterator

    Returns:
        Iterable[Dict[str,Any]]:
            an iterator of key-value records

    """
    return iter(_KeyValueIterator(itr))

class _KeyValueIterator:
    """
    An iterable of objects of key-value records that wraps an underlying gRPC stream
    of _kvdb_pb2.Records.

    Args:
        itr (grpc._channel._MultiThreadedRendezvous): the underlying stream
        
    """
    def __init__(self, itr):
        # record the underlying record iterator
        self.itr = itr
    
    def __iter__(self):
        try:
            for x in self.itr:
                yield _from_record(x)
        except GeneratorExit:
            # the iterator was explicitly closed, so we close the underlying stream
            self.itr.cancel()
        else:
            # Grab the trailer metadata
            md = self.itr.trailing_metadata()
            # Raise an exception if there was any error there
            _examine_trailer_metadata(md)

def _to_index(s):
    """
    Converts the given string to a _kvdb_pb2.Index.

    Args:
        s (str):
            the key
        
    Returns:
        _kvdb_pb2.Index

    Raises:
        ValueError: 
            if an illegal key name is passed

    """
    # Sanity check
    if not isinstance(s, str):
        raise TypeError("expected a string")
    # Convert the string
    result = Index()
    result.index = s
    return result

def _from_index_list(S):
    """
    Converts the given _kvdb_pb2.IndexList to a list of strings.

    Args:
        S (_kvdb_pb2.IndexList):
            the indices to convert
        
    Returns:
        List[str]

    """ 
    return [ idx.index for idx in S.list ]

def _to_key_list(keys):
    """
    Converts the given list of keys to a _kvdb_pb2.KeyList.

    Args:
        keys (List[str]):
            the keys to convert
    
    Returns:
        _kvdb_pb2.KeyList

    """
    result = KeyList()
    result.list.extend([Key(key=k) for k in keys])
    return result