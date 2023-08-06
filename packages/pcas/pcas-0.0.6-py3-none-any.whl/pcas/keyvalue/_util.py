"""
Utility functions for the keyvalue package.
"""

# To the extent possible under law, the author(s) have dedicated all copyright and
# related and neighboring rights to this software to the public domain worldwide.
# This software is distributed without any warranty.
#     
# You should have received a copy of the CC0 Public Domain Dedication along with
# this software. If not, see <http://creativecommons.org/publicdomain/zero/1.0/>.

def _validate_table_name(s):
    """
    Validates the given table name.
    
    Args:
        s (str):
            the table name

    Raises:
        ValueError:
            if validation fails
    
    Returns:
        None
    
    """
    if not isinstance(s, str):
        raise TypeError("the table name should be a string")
    if not s:
        raise ValueError("the table name cannot be empty")

def _validate_key(s):
    """
    Validates the given key.
    
    Raises:
        ValueError:
            if validation fails
    
    Returns:
        None
    
    """
    if not isinstance(s, str):
        raise TypeError("the key should be a string")
    if not s:
        raise ValueError("the key cannot be empty")
