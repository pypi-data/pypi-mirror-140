"""
Describes a sort order.

"""

# To the extent possible under law, the author(s) have dedicated all copyright and
# related and neighboring rights to this software to the public domain worldwide.
# This software is distributed without any warranty.
#     
# You should have received a copy of the CC0 Public Domain Dedication along with
# this software. If not, see <http://creativecommons.org/publicdomain/zero/1.0/>.

from enum import Enum
from .exceptions import InvalidConditionError
from ..keyvalue.record import is_key

__all__ = [
    "Direction",
    "Order",
    "ascending",
    "descending",
]

class Direction(Enum):
    """Defines the sort direction."""
    ASCENDING = 0
    DESCENDING = 1

    def __str__(self):
        if self.is_ascending():
            return "ASC"
        return "DESC"

    def is_ascending(self):
        """Returns true iff the sort direction is ascending.≈"""
        return self == Direction.ASCENDING
    
    def is_descending(self):
        """Returns true iff the sort direction is descending.≈"""
        return self == Direction.DESCENDING


class Order:
    """
    Describes the sort direction for a key.
    
    Args:
        key (str): the key on which to sort
        direction (Direction): the direction
        
    """
    def __init__(self, key, direction):
        if not isinstance(key, str):
            raise TypeError("expected a string")
        if not isinstance(direction, Direction):
            raise TypeError("expected a direction")
        self._key = key
        self._direction = direction
    
    def __str__(self):
        return self._key + " " + str(self._direction)
    
    def __eq__(self, other):
        if not isinstance(self, Order):
            return False
        return self._key == other._key and self._direction == other._direction

    def is_ascending(self):
        """Returns true iff the sort direction is ascending."""
        return self._direction.is_ascending()

    def is_descending(self):
        """Returns true iff the sort direction is descending."""
        return self._direction.is_descending()

    def key(self):
        """Returns the sort key."""
        return self._key

    def validate(self):
        """
        Raises an InvalidConditionError unless self.key satisfies
        pcas.keyvalue.record.is_key.
        
        Returns:
            None
            
        """
        if not is_key(self._key):
            raise InvalidConditionError('malformed key: {}'.format(self._key))

def ascending(key):
    """
    Returns a sort order that is ascending on the given key.
    
    Args:
        key (string): the sort key
    
    """
    if not isinstance(key, str):
        raise TypeError("the key must be a string")
    return Order(key, Direction.ASCENDING)

def descending(key):
    """
    Returns a sort order that is descending on the given key.
    
    Args:
        key (string): the sort key
    
    """
    if not isinstance(key, str):
        raise TypeError("the key must be a string")
    return Order(key, Direction.DESCENDING)

