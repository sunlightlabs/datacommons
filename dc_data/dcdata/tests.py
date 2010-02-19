

from unittest import TestCase
from django.db import connection

from updates import edits, update
from dcdata.contribution.sources.crp import FILE_TYPES
from dcdata.loading import model_fields
from scripts.crp.denormalize_indiv import CRPIndividualDenormalizer


class TestCRPDenormalization(TestCase):
    def test_crp_individual_record_processing(self):
        denormalizer = CRPIndividualDenormalizer({}, {}, {})
        
        input_values = ["2000","0011161","f0000263005 ","VAN SYCKLE, LORRAINE E","C00040998","","","T2300","02/22/1999","200","","BANGOR","ME","04401","PB","15 ","C00040998","","F","VAN SYCKLE LM","99034391444","","","P/PAC"]
        input_record = dict(zip(FILE_TYPES['indivs'], input_values))
        
        output_record = denormalizer.process_record(input_record)

        self.assertEqual(set(model_fields('contribution.Contribution')), set(output_record.keys()))
        

# tests the experimental 'updates' module
class TestUpdates(TestCase):
    def create_table(self, table_name):
        self.cursor.execute("""create table %s ( \
                    id int not null, \
                    name varchar(255), \
                    age int, \
                    primary key (id))
                      """ % table_name)
        
    def drop_table(self, table_name):
        self.cursor.execute("drop table %s" % table_name)
        
    def insert_record(self, table_name, id, name, age):
        self.cursor.execute("insert into %s (id, name, age) values ('%s', '%s', '%s')" % (table_name, id, name, age))
        
    
    def setUp(self):
        self.cursor = connection.cursor()
        
        self.create_table('old_table')
        self.create_table('new_table')
        
    def tearDown(self):
        self.drop_table('old_table')
        self.drop_table('new_table')
        
    
    def test_edits_empty(self):
        (inserts, updates, deletes) = edits('old_table', 'new_table', 'id', ('name', 'age'))

        self.assertEqual(set([]), set(inserts))
        self.assertEqual(set([]), set(updates))
        self.assertEqual(set([]), set(deletes))
        
        update('old_table', 'new_table', 'id', ('name', 'age'))
        self.assertTablesEqual()
        

    def test_edits_empty_new(self):
        self.insert_record('old_table', 1, 'Jeremy', 29)
        self.insert_record('old_table', 2, 'Ethan', 28)
        self.insert_record('old_table', 3, 'Clay', 35)
        
        (inserts, updates, deletes) = edits('old_table', 'new_table', 'id', ('name', 'age'))

        self.assertEqual(set([]), set(inserts))
        self.assertEqual(set([]), set(updates))
        self.assertEqual(set([(1,),(2,),(3,)]), set(deletes))
        
        update('old_table', 'new_table', 'id', ('name', 'age'))
        self.assertTablesEqual()

    def test_edits_empty_old(self):
        self.insert_record('new_table', 1, 'Jeremy', 29)
        self.insert_record('new_table', 2, 'Ethan', 28)
        self.insert_record('new_table', 3, 'Clay', 35)
        
        (inserts, updates, deletes) = edits('old_table', 'new_table', 'id', ('name', 'age'))

        self.assertEqual(set([(1L, u'Jeremy', 29L), (2L, u'Ethan', 28L), (3L, u'Clay', 35L)]), set(inserts))
        self.assertEqual(set([]), set(updates))
        self.assertEqual(set([]), set(deletes))     
        
        update('old_table', 'new_table', 'id', ('name', 'age'))
        self.assertTablesEqual()   
        
        
    def test_edits(self):
        self.insert_record('old_table', 1, 'Jeremy', 29)
        self.insert_record('old_table', 2, 'Ethan', 28)
        self.insert_record('old_table', 3, 'Clay', 35)
        
        self.insert_record('new_table', 2, 'Ethan', 29)
        self.insert_record('new_table', 3, 'Clay', 35)
        self.insert_record('new_table', 4, 'Garrett', 35)

        (inserts, updates, deletes) = edits('old_table', 'new_table', 'id', ('name', 'age'))
        
        self.assertEqual(set([(4L, u'Garrett', 35L)]), set(inserts))
        self.assertEqual(set([(1,)]), set(deletes))
        self.assertEqual(set([(2L, u'Ethan', 29L)]), set(updates))
        
        update('old_table', 'new_table', 'id', ('name', 'age'))
        self.assertTablesEqual()


    def assertTablesEqual(self):
        new_table_cursor = connection.cursor()
        updated_table_cursor = connection.cursor()
        
        new_table_cursor.execute("select * from new_table order by id")        
        updated_table_cursor.execute("select * from old_table order by id")
        
        for (new_row, updated_row) in map(None, new_table_cursor, updated_table_cursor):
            self.assertEqual(new_row, updated_row)
            