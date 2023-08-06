"""
Defines an object representing a table in a pcas keyvalue database.
"""

# To the extent possible under law, the author(s) have dedicated all copyright and
# related and neighboring rights to this software to the public domain worldwide.
# This software is distributed without any warranty.
#     
# You should have received a copy of the CC0 Public Domain Dedication along with
# this software. If not, see <http://creativecommons.org/publicdomain/zero/1.0/>.

from ._util import _validate_table_name
from .exceptions import TableClosedError

class Table:
    """A class that represents a table in a pcas keyvalue database. 
    
    """

    def __init__(self, conn, name):
        """
        Create the table.
        
        Args:
            conn (keyvalue.Connection):
                The underlying connection
            name (str):
                The name of the table

        Raises:
            ConnectionClosedError:
                if the connection is closed
            ValueError:
                if invalid arguments are passed

        """
        # Validate the table name
        _validate_table_name(name)
        # Record the connection and the database name
        self._conn = conn
        self._name = name
        # Record that we are not closed
        self._is_closed = False

    def __del__(self):
        """
        Closes the table when it is garbage collected.
        """
        self.close()

    def add_index(self, key):
        """
        Add an index on the given key.
        
        Args:
            key (str): the key
        
        Returns:
            None

        Raises:
            ConnectionClosedError:
                if the underlying connection to the database is closed
            ServerError:
                if a server error occurred
            TableClosedError: 
                if the table is closed
            ValueError:
                if an empty key is passed

        """
        if self._is_closed:
            raise TableClosedError
        return self._conn._add_index(self._name, key)

    def add_keys(self, rec):
        """
        Updates each record r in the table with the given name, adding any keys
        in rec that are not already present along with the corresponding values.
        Any keys that are already present in r will be left unmodified.
        
        Args:
            rec (Dict[str,Any]):
                the keys to insert, and the corresponding values
        
        Returns:
            None

        Raises:
            ConnectionClosedError:
                if the connection is closed
            ServerError:
                if a server error occurred
            TableClosedError: 
                if the table is closed
            ValueError:
                if an empty key is passed

        """
        if self._is_closed:
            raise TableClosedError
        return self._conn._add_keys(self._name, rec)

    def add_unique_index(self, key):
        """
        Add an index on the given key and the constraint that, for each value
        of this key, there is at most one record with that value.
        
        Args:
            key (str): the key
        
        Returns:
            None

        Raises:
            ConnectionClosedError:
                if the underlying connection to the database is closed
            ServerError:
                if a server error occurred
            TableClosedError: 
                if the table is closed
            ValueError:
                if an empty key is passed

        """
        if self._is_closed:
            raise TableClosedError
        return self._conn._add_unique_index(self._name, key)

    def close(self):
        """Close the table, preventing further operations."""
        if not self._is_closed:
            self._is_closed = True
            del self._conn

    def count(self, condition=None):
        """
        Return the number of records in the table that satisfy the given condition.
        The SQL format for condition is documented in the sql package. If the 
        condition is omitted then all records in the table are counted.

        Args:
            condition (Optional[Union[str,Dict[str,Any]]]):
                the condition, in SQL format or as a key-value record
        
        Returns:
            int: 
                the number of records
        
        Raises:
            ConnectionClosedError:
                if the underlying connection to the database is closed
            pcas.sql.exceptions.InvalidConditionError: 
                if the condition is invalid
            pcas.sql.exceptions.ParseError: 
                if the condition fails to parse
            pcas.sql.exceptions.ScanError:  
                if the condition fails to parse
            ServerError:
                if a server error occurred
            TableClosedError: 
                if the table is closed
            TypeError:  
                if record conversion is not possible
            ValueError: 
                if an illegal value is encountered

        """
        if self._is_closed:
            raise TableClosedError
        elif condition is None:
            condition = "WHERE TRUE"
        return self._conn._count_where(self._name, condition)
    
    def delete(self, condition=None):
        """
        Deletes those records in the table that match "selector". Returns the number
        of records deleted. 
        
        The SQL format for condition is documented in the sql package. If the
        condition is omitted then all records in the table are deleted.

        Args:
            condition (Optional[Union[str,Dict[str,Any]]]):
                the condition, in SQL format or as a key-value record
        
        Returns:
            int: 
                the number of records deleted
        
        Raises:
            ConnectionClosedError:
                if the underlying connection to the database is closed
            pcas.sql.exceptions.InvalidConditionError: 
                if the condition is invalid
            pcas.sql.exceptions.ParseError: 
                if the condition fails to parse
            pcas.sql.exceptions.ScanError:  
                if the condition fails to parse
            ServerError:
                if a server error occurred
            TableClosedError: 
                if the table is closed
            TypeError:  
                if record conversion is not possible
            ValueError: 
                if an illegal value is encountered

        """
        if self._is_closed:
            raise TableClosedError
        elif condition is None:
            condition = "WHERE TRUE"
        return self._conn._delete_where(self._name, condition)

    def delete_index(self, key):
        """
        Deletes the index on the given key. If no index is present, this is a nop.
        
        Args:
            key (str): the key
        
        Returns:
            None

        Raises:
            ConnectionClosedError:
                if the underlying connection to the database is closed
            ServerError:
                if a server error occurred
            TableClosedError: 
                if the table is closed
            ValueError:
                if an empty key is passed

        """
        if self._is_closed:
            raise TableClosedError
        return self._conn._delete_index(self._name, key)

    def delete_keys(self, keys):
        """
        Updates all records in the table, deleting the specified keys if
        present.
        
        Args:
            keys (List[str]): 
                the keys to delete
        
        Returns:
            None

        Raises:
            ConnectionClosedError:
                if the connection is closed
            ServerError:
                if a server error occurred
            TableClosedError: 
                if the table is closed
            ValueError:
                if an empty key is passed

        """
        if self._is_closed:
            raise TableClosedError
        return self._conn._delete_keys(self._name, keys)

    def describe(self):
        """
        Return a best-guess template for the data in the table. 

        Returns:
            Dict[str, Any]: 
                A template for records in the table
        
        Raises:
            ConnectionClosedError:
                if the underlying connection to the database is closed
            ServerError:
                if a server error occurred
            TableClosedError: 
                if the table is closed
            TypeError:
                if template conversion is not possible
            ValueError:
                if an illegal value is encountered

        """
        if self._is_closed:
            raise TableClosedError
        return self._conn.describe_table(self._name)

    def insert(self, records):
        """
        Insert the given records into the table.

        Args:
            records (Iterable[Dict[str,Any]]):  The records
        
        Returns:
            None

        Raises:
            ConnectionClosedError:
                if the underlying connection to the database is closed
            ServerError:
                if a server error occurred
            TableClosedError:
                if the table is closed
            TypeError:
                if record conversion is not possible
            ValueError:
                if an illegal value is encountered


        """
        if self._is_closed:
            raise TableClosedError
        return self._conn._insert(self._name, records)
    
    def list_indices(self):
        """
        Returns a list of the keys for which indices are present.
        
        Returns:
            List[str]: the keys for which indices are present

        Raises:
            ConnectionClosedError:
                if the underlying connection to the database is closed
            ServerError:
                if a server error occurred
            TableClosedError: 
                if the table is closed

        """
        if self._is_closed:
            raise TableClosedError
        return self._conn._list_indices(self._name)

    def name(self):
        """The name of the table."""
        return self._name

    def update(self, replacement, condition=None):
        """
        Updates all records in the table that satisfy the given condition by
        setting the keys in "replacement" to the given values. If the condition
        is omitted then all records in the table are updated.

        The SQL format for condition is documented in the sql package.

        Args:
            replacement (Dict[str, Any]): 
                a record containing the key-value pairs to update
            condition (Optional[Union[str,Dict[str,Any]]]):
                the condition, in SQL format or as a key-value record

        Returns:
            int: 
                the number of records updated
        
        Raises:
            ConnectionClosedError:
                if the underlying connection to the database is closed
            pcas.sql.exceptions.InvalidConditionError: 
                if the condition is invalid
            pcas.sql.exceptions.ParseError: 
                if the condition fails to parse
            pcas.sql.exceptions.ScanError:  
                if the condition fails to parse
            ServerError:
                if a server error occurred
            TableClosedError: 
                if the table is closed
            TypeError:  
                if record conversion is not possible
            ValueError: 
                if an illegal value is encountered
       
        """
        if self._is_closed:
            raise TableClosedError
        elif condition is None:
            condition = "WHERE TRUE"
        return self._conn._update_where(self._name, replacement, condition)

    def select(self, template, selector=None, order=None, limit=None):
        """
        Returns an iterator of records matching the given selector. The records will
        be in the form specified by the given template. If an order is provided, the
        records will be returned in that order. If a limit is provided, it must be
        positive and at most that many records will be returned.

        If the selector is provided as a string in SQL format then it may also specify the order and/or the limit. If it does so then order, and/or respectively limit, must either be unspecified or specified as None.

        If the selector is omitted, all records in the table will be returned.

        The iterator returned will raise a ServerError on iteration if a server
        error occurs.

        Args:
            template (Dict[str,Any]):
                the template for returned records, as a key-value record
            selector (Optional[Union[str,Dict[str,Any]]]):
                the condition to match, as a string in SQL format or a key-value record
            order (Optional[pcas.sql.sort.Order]):
                the order for the records
            limit (Optional[int]):
                the maximum number of records to return
            
        Returns:
            Iterator[Dict[str, Any]]

        Raises:
            ConnectionClosedError:
                if the underlying connection to the database is closed
            pcas.sql.exceptions.InvalidConditionError: 
                if the condition is invalid
            pcas.sql.exceptions.ParseError: 
                if the condition fails to parse
            pcas.sql.exceptions.ScanError:  
                if the condition fails to parse
            TableClosedError: 
                if the table is closed
            TypeError:  
                if record conversion is not possible
            ValueError: 
                if an illegal value is encountered

        """
        if self._is_closed:
            raise TableClosedError
        elif selector is None:
            selector = "WHERE TRUE"
        return self._conn._select_where_limit(self._name, template, selector, order, limit)