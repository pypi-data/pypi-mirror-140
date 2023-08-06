"""
Defines functions to validate key-value records.

"""

# To the extent possible under law, the author(s) have dedicated all copyright and
# related and neighboring rights to this software to the public domain worldwide.
# This software is distributed without any warranty.
#     
# You should have received a copy of the CC0 Public Domain Dedication along with
# this software. If not, see <http://creativecommons.org/publicdomain/zero/1.0/>.

def is_key(k):
    """
    Returns true if and only if the string k has the format required for a key.
    
    That is, returns true if and only if k matches [a-zA-Z]+[a-zA-Z0-9_]*.
    """
    if not isinstance(k, str):
        raise ValueError("expected a string")
    if len(k)==0:
        return False
    if not ('a' <= k[0] <= 'z' or 'A' <= k[0] <= 'Z'):
        return False
    for c in k[1:]:
        if not ('a' <=c <= 'z' or 'A' <= c <= 'Z' or '0' <= c <= '9' or c =='_'):
            return False
    return True

def is_value(v):
    """
    Returns true if and only if v is an instance of a type that can occur as 
    a value in a Record. That is, returns true if and only if v is an integer, 
    boolean, float, string, or bytes.
    
    """
    return (isinstance(v, int) or 
            isinstance(v, bool) or
            isinstance(v, float) or
            isinstance(v, str) or
            isinstance(v, bytes))