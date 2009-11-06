

import unittest

#from django.db import connection
from MySQLdb import connect


from updates import edits

class Tests(unittest.TestCase):
    def create_table(self, table_name):
        self.cursor.execute("""create table `%s` ( \
                    id int not null, \
                    name varchar(255), \
                    age int, \
                    primary key (id))
                      """ % table_name)
        
    def insert_record(self, table_name, id, name, age):
        self.cursor.execute("insert into `%s` (id, name, age) values ('%s', '%s', '%s')" % (table_name, id, name, age))
        
    
    def setUp(self):
        self.cursor = connect(host="localhost", user="root", db="test_datacommons").cursor()
        
        self.create_table('old_table')
        self.create_table('new_table')
            
        
    def test_edits(self):
        self.insert_record('old_table', 1, 'Jeremy', 29)
        self.insert_record('old_table', 2, 'Ethan', 28)
        self.insert_record('old_table', 3, 'Clay', 35)
        
        self.insert_record('new_table', 2, 'Ethan', 29)
        self.insert_record('new_table', 3, 'Clay', 35)
        self.insert_record('new_table', 4, 'Garrett', 35)

        (inserts, updates, deletes) = edits('old_table', 'new_table', 'id', ('name', 'age'))
        
        self.assertEqual([4], inserts)
        self.assertEqual([1], deletes)
        self.assertEqual([(2L, u'Ethan', 29L)], updates)
