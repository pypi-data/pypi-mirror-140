"""
Integration tests for the keyvalue package.

"""

# To the extent possible under law, the author(s) have dedicated all copyright and
# related and neighboring rights to this software to the public domain worldwide.
# This software is distributed without any warranty.
#     
# You should have received a copy of the CC0 Public Domain Dedication along with
# this software. If not, see <http://creativecommons.org/publicdomain/zero/1.0/>.

from pcas.keyvalue.exceptions import ServerError
import unittest
import uuid
from .. import Connection

# The database and table to use for the tests
# Note that data in this table will be modified and/or deleted during the test.
_TEST_DB = "pcas-python-keyvalue-integration-test"
_TEST_TABLE = "example"

class TestIntegration(unittest.TestCase):
    """
    These tests will connect to a pcas kvdbd server at the address and port 
    specified by the environment variable PCAS_KVDB_ADDRESS. If this enviroment
    variable is not set then it will connect to a pcas kvdbd server running on
    localhost:12356. 
    
    WARNING: Data in the table "example" in the database 
    "pcas-python-keyvalue-integration-test" hosted on that server will be modified
    and/or destroyed by these tests.
    """
    def setUp(self):
        self.c = Connection(_TEST_DB)
        # delete the table, if it exists
        self.c.delete_table(_TEST_TABLE)
        
    def tearDown(self):
        self.c.close()
    
    def test_integration(self):
        # Create the table
        template = {'a':0, 'b': ''}
        self.c.create_table(_TEST_TABLE, template)
        # The table should appear in the list of tables
        self.assertIn(_TEST_TABLE, self.c.list_tables())
        # Creating the table twice should fail
        with self.assertRaises(ServerError):
            self.c.create_table(_TEST_TABLE, template)
        # There should be zero elements in the table
        t = self.c.connect_to_table(_TEST_TABLE)
        self.assertEqual(0, t.count())
        # Insert some elements into the table
        vals = [
            {'a': 5, 'b': 'hello'},
            {'a': 6, 'b': 'world'},
        ]
        t.insert(vals)
        self.assertEqual(len(vals), t.count())
        # Iterate over the elements in the table
        for x in t.select(template):
            self.assertIn(x['a'], [5,6])
            if x['a'] == 5:
                self.assertEqual(x['b'], "hello")
            else:
                self.assertEqual(x['b'], "world")
        # Iterate over exactly one element in the table
        count = 0
        for x in t.select(template, "ORDER BY a LIMIT 1"):
            self.assertEqual(x, vals[0])
            count += 1
        self.assertEqual(count, 1)
        # Update the element with a = 5 to have an extra piece of data
        self.assertEqual(1, t.update({'c': bytes('today', 'utf-8')}, "WHERE a=5"))
        # Test describe_table
        # Note that MongoDB can't tell the difference between strings and slices of bytes, so we need to test this as an 'assertIn' because we don't know the backend being used.
        self.assertIn(t.describe(), [
            {'a':0, 'b':'', 'c': ""}, 
            {'a':0, 'b':'', 'c': bytes()}, 
        ])
        # Iterate over the elements in the table again
        new_template = template
        new_template['c'] = bytes()
        for x in t.select(new_template):
            self.assertIn(x['a'], [5,6])
            if x['a'] == 5:
                y = vals[0]
                y['c'] = bytes('today', 'utf-8')
                self.assertEqual(x, y)
            else:
                self.assertEqual(x, vals[1])
        # Delete the element with a=5
        self.assertEqual(1, t.delete("WHERE a=5"))
        # Count the number of elements in the table
        self.assertEqual(1, t.count())
        # Delete the element with a=6
        self.assertEqual(1, t.delete("WHERE a=6"))
        # Count the number of elements in the table
        self.assertEqual(0, t.count())
        # Delete the table
        self.c.delete_table(_TEST_TABLE)


    def test_indices(self):
        # Create the table
        template = {'id':0, 'fish': 'chips'}
        self.c.create_table(_TEST_TABLE, template)
        t = self.c.connect_to_table(_TEST_TABLE)
        # Add some data to the table
        t.insert([
            {'id':1, 'fish': 'yes'},
            {'id':2, 'fish': 'yes'},
            {'id':3, 'fish': 'no'},
        ])
        # There should be no indices on the table
        self.assertEqual([], t.list_indices())
        # Add a unique index 
        t.add_unique_index('id')
        self.assertEqual(['id'], t.list_indices())
        # Add an index on a non-existing key
        t.add_index('peas')
        self.assertSetEqual(set(['id', 'peas']), set(t.list_indices()))
        # Delete an index
        t.delete_index('id')
        self.assertEqual(['peas'], t.list_indices())
        # Add an index on an existing key
        t.add_index('fish')
        self.assertSetEqual(set(['fish', 'peas']), set(t.list_indices()))
        # Delete the table
        self.c.delete_table(_TEST_TABLE)

    def test_add_delete_keys(self):
        # Delete the table, if it exists
        self.c.delete_table(_TEST_TABLE)
        # Create the table
        template = {'a': 0,'b': ''}
        self.c.create_table(_TEST_TABLE, template)
        t = self.c.connect_to_table(_TEST_TABLE)
        # Add some data to the table
        recs = [
            {'a': 0, 'b': 'alpha'},
            {'a': 1},
            {'a': 2, 'b': 'gamma'}
        ]
        t.insert(recs)
        # Insert completely new keys
        inserter = {'c':7, 'd': True}
        t.add_keys(inserter)
        template['c'] = 0
        template['d'] = False
        # Check that the new values are correct
        for r in t.select(template):
            idx = r['a']
            expected = {k:v for k, v in recs[idx].items()}
            expected['c'] = 7
            expected['d'] = True
            self.assertEqual(expected, r)
        # Delete the new keys
        t.delete_keys(['c', 'd'])
        del template['c']
        del template['d']
        self.assertEqual(template, t.describe())
        # Check the values again
        for r in t.select(template):
            idx = r['a']
            self.assertEqual(recs[idx], r)
        # Add a partially-existing key
        inserter = {'b': 'beta'}
        t.add_keys(inserter)
        self.assertEqual(template, t.describe())
        # Check the values
        for r in t.select(template):
            idx = r['a']
            if idx != 1:
                self.assertEqual(recs[idx], r)
            else:
                expected = {'a':1, 'b':'beta'}
                self.assertEqual(expected, r)
        # Delete the table
        self.c.delete_table(_TEST_TABLE)

    def test_rename_table(self):
        # Delete the table, if it exists
        self.c.delete_table(_TEST_TABLE)
        # Get the list of table names
        L = self.c.list_tables()
        self.assertFalse(_TEST_TABLE in L)
        # Create the table
        template = {'a': 0,'b': ''}
        self.c.create_table(_TEST_TABLE, template)
        t = self.c.connect_to_table(_TEST_TABLE)
        # Populate the table
        t.insert([
            {'a': 0, 'b': 'alpha'},
            {'a': 1},
            {'a': 2, 'b': 'gamma'}
        ])
        # Check the list of tables again
        L.add(_TEST_TABLE)
        self.assertEqual(L, self.c.list_tables())
        # Rename the table
        u = str(uuid.uuid4())
        self.c.rename_table(_TEST_TABLE, u)
        # Check the list of tables again
        L.remove(_TEST_TABLE)
        L.add(u)
        self.assertEqual(L, self.c.list_tables())
        # Delete the table
        self.c.delete_table(u)
        # Check the list of tables again
        L.remove(u)
        self.assertEqual(L, self.c.list_tables())
