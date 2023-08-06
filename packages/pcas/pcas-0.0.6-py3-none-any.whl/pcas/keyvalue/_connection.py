"""
Defines an object representing a connection to a pcas kvdb server.
"""

# To the extent possible under law, the author(s) have dedicated all copyright and
# related and neighboring rights to this software to the public domain worldwide.
# This software is distributed without any warranty.
#     
# You should have received a copy of the CC0 Public Domain Dedication along with
# this software. If not, see <http://creativecommons.org/publicdomain/zero/1.0/>.

import grpc
import os

from ._kvdb_pb2_grpc import KvdbStub
from . import _convert
from ._kvdb_pb2 import NameAndTemplate, Name, SrcAndDstNames
from google.protobuf.empty_pb2 import Empty
from ._table import Table
from ._util import _validate_table_name, _validate_key
from .exceptions import ConnectionClosedError
from .. import PCAS_ROOT_CERTIFICATE

# MAX_MESSAGE_SIZE is the maximum message size, in bytes
MAX_MESSAGE_SIZE = 16 * 1024 * 1024 # 16Mb

class Connection:

    def __init__(self, db, address=None, certificate=None, app_name='python'):
        """
        Represents a connection to a pcas keyvalue server. 
        
        Args:
            db (str):
                The name of the database
            address (Optional[str]):
                The address of the PCAS keyvalue server
            certificate (Optional[str]):    
                The SSL certificate
            app_name (Optional[str]):
                The name by which to identify ourselves to the server

        If the address parameter is None, its value will be read from the
        environment variable "PCAS_KVDB_ADDRESS". If the certificate is None,
        its value will be read from the environment variable "PCAS_SSL_CERT".

        Raises:
            ValueError:
                if invalid arguments are passed

        """
        if not isinstance(db, str):
            raise TypeError("the database name should be a string")
        if not isinstance(address, str) and not address is None:
            raise TypeError("address should be a string")
        if not isinstance(certificate, str) and not certificate is None:
            raise TypeError("certificate should be a string")
        if not isinstance(app_name, str):
            raise TypeError("app_name should be a string")
        # Record the name of the database
        if not db.strip():
            raise ValueError("the database name must be non-empty")
        # Populate the address and certificate, unless they were passed to us
        if address is None:
            address = os.environ.get("PCAS_KVDB_ADDRESS", "")
        if certificate is None:
            certificate = os.environ.get("PCAS_SSL_CERT", "").strip().encode() + b'\n'
        # We trust any certificate signed by the PCAS root signing key
        certificate = certificate + PCAS_ROOT_CERTIFICATE
        # Create the gRPC channel
        creds = grpc.ssl_channel_credentials(root_certificates=certificate)
        opts=[
            ('grpc.max_send_message_length', MAX_MESSAGE_SIZE),
            ('grpc.max_receive_message_length', MAX_MESSAGE_SIZE),
        ]
        channel = grpc.secure_channel(address, creds, options=opts)
        self._stub = KvdbStub(channel)
        self._channel = channel
        self._is_closed = False
        # Record the app name and the database name
        self.app_name = app_name
        self.db = db

    def __del__(self):
        """Closes the connection when it is garbage collected."""
        self.close()

    def close(self):
        """Close the connection."""
        if not self._is_closed:
            self._is_closed = True
            self._channel.close()

    def connect_to_table(self, name):
        """
        Connect to the table with the given name.
        
        Args:
            name (str):
                The name of the table
        
        Raises:
            ConnectionClosedError:
                if the connection is closed
            ValueError:
                if an invalid name is passed

        """
        if self._is_closed:
            raise ConnectionClosedError
        # Validate the table name
        _validate_table_name(name)
        return Table(self, name)

    def create_table(self, name, template):
        """
        Create a table with the given name and template.

        The template must contain only values that are permissible
        in a keyvalue record.

        Args:
            name (str):
                The name of the table
            template (Dict[str, Any]):
                A template for records in the table
        
        Returns:
            None

        Raises:
            ConnectionClosedError:
                if the connection is closed
            ServerError:
                if a server error occurred
            TypeError:
                if template conversion is not possible
            ValueError:
                if invalid arguments are passed

        """
        if self._is_closed:
            raise ConnectionClosedError
        # Validate the table name
        _validate_table_name(name)
        # Create the NameAndTemplate
        nt = NameAndTemplate(
            name=name, 
            template=_convert._to_record(template),
        )
        # Make the request
        resp = self._stub.CreateTable.with_call(
            nt,
            metadata=(
                ('db_name', self.db),
                ('app_name', self.app_name),
            ))
        # Grab the call metadata
        md = resp[1]
        # Check the trailer metadata for errors
        _convert._examine_trailer_metadata(md.trailing_metadata())

    def delete_table(self, name):
        if self._is_closed:
            raise ConnectionClosedError
        """
        Delete the table with the given name.

        Args:
            name (str):
                The name of the table
        
        Returns:
            None

        Raises:
            ConnectionClosedError:
                if the connection is closed
            ServerError:
                if a server error occurred
            ValueError:
                if an invalid name is passed

        """
        # Validate the table name
        _validate_table_name(name)
        # Make the request
        resp = self._stub.DeleteTable.with_call(
            Name(name=name),
            metadata=(
                ('db_name', self.db),
                ('app_name', self.app_name),
            ))
        # Grab the call metadata
        md = resp[1]
        # Check the trailer metadata for errors
        _convert._examine_trailer_metadata(md.trailing_metadata())

    def describe_table(self, name):
        """
        Return a best-guess template for the data in the table 
        with the given name.

        Args:
            name (str):
                The name of the table

        Returns:
            Dict[str, Any]: 
                A template for records in the table
        
        Raises:
            ConnectionClosedError:
                if the connection is closed
            ServerError:
                if a server error occurred        
            TypeError:
                if template conversion is not possible
            ValueError:
                if an illegal value is encountered

        """
        if self._is_closed:
            raise ConnectionClosedError
        # Validate the table name
        _validate_table_name(name)
        # Make the request
        resp = self._stub.DescribeTable.with_call(
            Empty(),
            metadata=(
                ('db_name', self.db),
                ('table_name', name),
                ('app_name', self.app_name),
            ))
        # Grab the template and call metadata
        template = resp[0]
        md = resp[1]
        # Check the trailer metadata for errors
        _convert._examine_trailer_metadata(md.trailing_metadata())
        # Convert the return value
        return _convert._from_record(template)

    def list_tables(self):
        """
        List the tables in the database.

        Returns:
            A set containing the names of tables in the database
        
        Raises:
            ConnectionClosedError:
                if the connection is closed
            ServerError:
                if a server error occurred

        """
        if self._is_closed:
            raise ConnectionClosedError
        # Make the request
        resp = self._stub.ListTables.with_call(
            Empty(),
            metadata=(
                ('db_name', self.db),
                ('app_name', self.app_name),
            ))
        # Extract the table names and call metadata
        tn = resp[0]
        md = resp[1]
        # Check the trailer metadata for errors
        _convert._examine_trailer_metadata(md.trailing_metadata())
        # Return the table names
        return set([ x for x in tn.name ])

    def rename_table(self, src, dst):
        if self._is_closed:
            raise ConnectionClosedError
        """
        Renames the table src to dst.

        Args:
            src (str):
                The name of the table to rename
            dst (src):
                The new name of the table
        
        Returns:
            None

        Raises:
            ConnectionClosedError:
                if the connection is closed
            ServerError:
                if a server error occurred
            ValueError:
                if an invalid name is passed

        """
        # Validate the table names
        _validate_table_name(src)
        _validate_table_name(dst)
        # Make the request
        resp = self._stub.RenameTable.with_call(
            SrcAndDstNames(src=src, dst=dst),
            metadata=(
                ('db_name', self.db),
                ('app_name', self.app_name),
            ))
        # Grab the call metadata
        md = resp[1]
        # Check the trailer metadata for errors
        _convert._examine_trailer_metadata(md.trailing_metadata())

    def _add_index(self, name, key):
        """
        Adds an index on the given key to the table with the given name.
        
        Args:
            name (str):
                the name of the table
            key (str): 
                the key
        
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
            raise ConnectionClosedError
        # Validate the input
        _validate_table_name(name)
        _validate_key(key)
        # Make the request
        resp = self._stub.AddIndex.with_call(
            _convert._to_index(key),
            metadata=(
                ('db_name', self.db),
                ('table_name', name),
                ('app_name', self.app_name),
            ))
        # Grab the call metadata
        md = resp[1]
        # Check the trailer metadata for errors and return
        _convert._examine_trailer_metadata(md.trailing_metadata())
        return

    def _add_keys(self, name, rec):
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
            raise ConnectionClosedError
        # Validate the input
        _validate_table_name(name)
        # Make the request
        resp = self._stub.AddKeys.with_call(
            _convert._to_record(rec),
            metadata=(
                ('db_name', self.db),
                ('table_name', name),
                ('app_name', self.app_name),
            ))
        # Grab the call metadata
        md = resp[1]
        # Check the trailer metadata for errors and return
        _convert._examine_trailer_metadata(md.trailing_metadata())
        return

    def _add_unique_index(self, name, key):
        """
        Adds to the table with the given name an index on the given key and the
        constraint that, for each value of this key, there is at most one record
        with that value..
        
        Args:
            name (str):
                the name of the table
            key (str): 
                the key
        
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
            raise ConnectionClosedError
        # Validate the input
        _validate_table_name(name)
        _validate_key(key)
        # Make the request
        resp = self._stub.AddUniqueIndex.with_call(
            _convert._to_index(key),
            metadata=(
                ('db_name', self.db),
                ('table_name', name),
                ('app_name', self.app_name),
            ))
        # Grab the call metadata
        md = resp[1]
        # Check the trailer metadata for errors and return
        _convert._examine_trailer_metadata(md.trailing_metadata())
        return

    def _count_where(self, name, condition):
        """
        Return the number of records in the table with the given name
        that satisfy the given condition. Assumes that the table name 
        is valid.
        
        The SQL format for condition is documented in the sql package.

        Args:
            name (str):
                the name of the table
            condition (Union[str,Dict[str,Any]]):
                the condition, in SQL format or as a key-value record
        
        Returns:
            int: the number of records
        
        Raises:
            ConnectionClosedError:
                if the connection is closed
            pcas.sql.exceptions.InvalidConditionError: 
                if the condition is invalid
            pcas.sql.exceptions.ParseError: 
                if the condition fails to parse
            pcas.sql.exceptions.ScanError:  
                if the condition fails to parse
            ServerError:
                if a server error occurred
            ValueError: 
                if invalid arguments are passed

        """
        if self._is_closed:
            raise ConnectionClosedError
        # Make the request
        resp = self._stub.CountWhere.with_call(
            _convert._to_condition(condition),
            metadata=(
                ('db_name', self.db),
                ('table_name', name),
                ('app_name', self.app_name),
            ))
        # Grab the number of records and call metadata
        nrecs = resp[0]
        md = resp[1]
        # Check the trailer metadata for errors
        _convert._examine_trailer_metadata(md.trailing_metadata())
        # Convert the return value
        return _convert._from_number_of_records(nrecs)

    def _delete_index(self, name, key):
        """
        Deletes the index on the given key in the table with the given name.
        If no such index is present, this is a nop.
        
        Args:
            name (str):
                the name of the table
            key (str): 
                the key
        
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
            raise ConnectionClosedError
        # Validate the input
        _validate_table_name(name)
        _validate_key(key)
        # Make the request
        resp = self._stub.DeleteIndex.with_call(
            _convert._to_index(key),
            metadata=(
                ('db_name', self.db),
                ('table_name', name),
                ('app_name', self.app_name),
            ))
        # Grab the call metadata
        md = resp[1]
        # Check the trailer metadata for errors and return
        _convert._examine_trailer_metadata(md.trailing_metadata())
        return

    def _delete_keys(self, name, keys):
        """
        Updates all records in the table, deleting the specified keys if
        present.
        
        Args:
            name (str):
                the name of the table
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
            raise ConnectionClosedError
        # Validate the input
        _validate_table_name(name)
        # Handle the trivial case
        if len(keys) == 0:
            return
        # Validate the keys
        for k in keys: 
            _validate_key(k)
        # Make the request
        resp = self._stub.DeleteKeys.with_call(
            _convert._to_key_list(keys),
            metadata=(
                ('db_name', self.db),
                ('table_name', name),
                ('app_name', self.app_name),
            ))
        # Grab the call metadata
        md = resp[1]
        # Check the trailer metadata for errors and return
        _convert._examine_trailer_metadata(md.trailing_metadata())
        return


    def _delete_where(self, name, condition):
        """
        Delete the records in the table with the given name that satisfy the given
        condition. Assumes that the table name is valid.
        
        The SQL format for condition is documented in the sql package.

        Args:
            name (str):
                the name of the table
            condition (Union[str,Dict[str,Any]]):
                the condition, in SQL format or as a key-value record
        
        Returns:
            int: the number of records
        
        Raises:
            ConnectionClosedError:
                if the connection is closed
            pcas.sql.exceptions.InvalidConditionError: 
                if the condition is invalid
            pcas.sql.exceptions.ParseError: 
                if the condition fails to parse
            pcas.sql.exceptions.ScanError:  
                if the condition fails to parse
            ServerError:
                if a server error occurred
            ValueError: 
                if invalid arguments are passed

        """
        if self._is_closed:
            raise ConnectionClosedError
        # Make the request
        resp = self._stub.DeleteWhere.with_call(
            _convert._to_condition(condition),
            metadata=(
                ('db_name', self.db),
                ('table_name', name),
                ('app_name', self.app_name),
            ))
        # Grab the number of records and the call metadata
        nrecs = resp[0]
        md = resp[1]
        # Check the trailer metadata for errors
        _convert._examine_trailer_metadata(md.trailing_metadata())
        # Convert the return value
        return _convert._from_number_of_records(nrecs)
        
    def _insert(self, name, records):
        """
        Insert the given records into the table with the given name. 
        Assumes that the table name is valid.

        Args:
            name (str):
                The name of the table
            records (Iterable[Dict[str,Any]]):
                The records
        
        Returns:
            None

        Raises:
            ConnectionClosedError:
                if the connection is closed
            ServerError:
                if a server error occurred
            TypeError:
                if record conversion is not possible
            ValueError:
                if an illegal value is encountered

        """
        if self._is_closed:
            raise ConnectionClosedError
        # Convert the iterator
        itr = _convert._to_record_iterator(records)
        # Make the request
        try:
            resp = self._stub.Insert.with_call(
                itr,
                metadata=(
                    ('db_name', self.db),
                    ('table_name', name),
                    ('app_name', self.app_name),
                ))
        except:
            # Check any error from iteration
            e = itr.last_exception()
            if e is not None:
                # gRPC intercepted this exception, so we raise it instead here
                raise e
            # The exception wasn't from our iterator, so we reraise it
            raise
        # Grab the call metadata
        md = resp[1]
        # Check the trailer metadata for errors
        _convert._examine_trailer_metadata(md.trailing_metadata())

    def _list_indices(self, name):
        """
        Returns a list of the keys in the table with the given name for which
        indices are present.
        
        Args:
            name (str):
                the name of the table
        
        Returns:
            List[str]:
                the keys for which indices are present

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
            raise ConnectionClosedError
        # Validate the input
        _validate_table_name(name)
        # Make the request
        resp = self._stub.ListIndices.with_call(
            Empty(),
            metadata=(
                ('db_name', self.db),
                ('table_name', name),
                ('app_name', self.app_name),
            ))
        # Grab the indices and the call metadata
        indices = resp[0] 
        md = resp[1]
        # Check the trailer metadata for errors and return
        _convert._examine_trailer_metadata(md.trailing_metadata())
        # Convert the return value
        return _convert._from_index_list(indices)

    def _select_where_limit(self, name, template, selector, order=None, limit=None):
        """ 
        Returns an iterator of records in the table with the given name that match
        the given condition. The records will be in the form specified by the given
        template. If an order is provided, the records will be returned in that order.
        If a limit is provided, it must be a positive integer and at most that many
        records will be returned.

        If the selector is provided as a string in SQL format then it may also specify the order and/or the limit. If it does so then order, and/or respectively limit, must either be unspecified or specified as None.

        Args:
            template (Dict[str,Any]):
                the template for returned records, as a key-value record
            selector (Union[str,Dict[str,Any]]):
                the condition to match, as a string in SQL format or a key-value record
            order (Optional[pcas.sql.sort.Order]):
                the order for the records
            limit (Optional[int]):
                the maximum number of records to return
            
        Returns:
            Iterator[Dict[str, Any]]

        Raises:
            ConnectionClosedError:
                if the connection is closed
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
        if self._is_closed:
            raise ConnectionClosedError
        resp = self._stub.SelectWhereLimit(
            _convert._to_condition_template_order_and_limit(template, selector, order, limit),
            metadata=(
                ('db_name', self.db),
                ('table_name', name),
                ('app_name', self.app_name),
            ))
        return _convert._from_record_iterator(resp)

    def _update_where(self, name, replacement, condition):
        """
        Updates all records in the table that satisfy the given condition by
        setting the keys in "replacement" to the given values. Assumes that 
        the table name is valid.

        The SQL format for condition is documented in the sql package.

        Args:
            name (str):
                the name of the table
            replacement (Dict[str, Any]):
                a record containing the key-value pairs to update
            condition (Union[str,Dict[str,Any]]):
                the condition, in SQL format or as a key-value record

        Returns:
            int:
                the number of records updated
        
        Raises:
            ConnectionClosedError:
                if the connection is closed
            pcas.sql.exceptions.InvalidConditionError: 
                if the condition is invalid
            pcas.sql.exceptions.ParseError: 
                if the condition fails to parse
            pcas.sql.exceptions.ScanError:  
                if the condition fails to parse
            ServerError:
                if a server error occurred
            TypeError:  
                if record conversion is not possible
            ValueError: 
                if an illegal value is encountered
       
        """
        if self._is_closed:
            raise ConnectionClosedError
        resp = self._stub.UpdateWhere.with_call(
            _convert._to_condition_and_replacement(condition, replacement),
            metadata=(
                ('db_name', self.db),
                ('table_name', name),
                ('app_name', self.app_name),
            ))
        # Grab the number of records and call metadata
        nrecs = resp[0]
        md = resp[1]
        # Check the trailer metadata for errors
        _convert._examine_trailer_metadata(md.trailing_metadata())
        # Convert the return value
        return _convert._from_number_of_records(nrecs)

