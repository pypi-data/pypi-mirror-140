"""
Defines a parser for SQL-formatted queries.

The SQL should be formatted as follows:

	[[WHERE] <where condition>] [ORDER BY <sort order>] [LIMIT <limit>]

Note that prefixing the WHERE condition with "WHERE" is currently optional, although this might change in the future.

* <where condition>

The following types are supported:
	string -	surrounded by matching double- (") or single-quotes (')
	integer -	must fit in a Golang int64 or uint64
	float -		must fit in a Golang float64
	boolean -	TRUE or FALSE
The following standard SQL operators are supported:
	=, !=
	<, >, <=, >=
	IS, IS NOT
	IN, NOT IN
	BETWEEN, NOT BETWEEN
	AND
	OR

* <sort order>

This should be formatted
	key1 [ASC | DESC], key2 [ASC | DESC], ..., keyn [ASC | DESC]
where ASC and DESC denote increasing and decreasing order, respectively. Precisely what this means is determined by the underlying storage engine and data type. If ASC or DESC is omitted, then ASC is assumed by default.

* <limit>

A non-negative integer (that must fit in a Golang int64) must be provided.

This is based on [https://bitbucket.org/pcas/keyvalue/src/master/parse/].

"""

# To the extent possible under law, the author(s) have dedicated all copyright and
# related and neighboring rights to this software to the public domain worldwide.
# This software is distributed without any warranty.
#     
# You should have received a copy of the CC0 Public Domain Dedication along with
# this software. If not, see <http://creativecommons.org/publicdomain/zero/1.0/>.

from .condition import (
	Condition,
    LeafOp,
    Bool,
    TRUE,
    FALSE,
    AndOp,
    BetweenOp,
    EqualOp,
    GreaterThanOp,
    GreaterThanOrEqualToOp,
    InOp,
    IsOp,
    LessThanOp,
    LessThanOrEqualToOp,
    NotBetweenOp,
    NotEqualOp,
    NotInOp,
    OrOp,
    condition_from_record,
)

from ._parser import (
	parse_condition,
	parse_order,
	parse_query,
)

from .sort import (
	Direction,
	Order,
	ascending,
	descending,
)

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
	"Direction",
	"Order",
	"ascending",
	"descending",
    "condition_from_record",
	"parse_condition",
	"parse_order",
	"parse_query",
]