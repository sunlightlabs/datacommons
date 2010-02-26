
import os
from unittest import TestCase
from django.db import connection

from updates import edits, update
from dcdata.contribution.sources.crp import FILE_TYPES
from dcdata.loading import model_fields
from django.core.management import call_command
from dcdata.management.commands.crp_denormalize_individuals import CRPDenormalizeIndividual
from dcdata.contribution.models import Contribution
from dcdata.processor import load_data


class TestCRPDenormalizeAll(TestCase):
    
    def test_denormalize_and_load(self):
        if os.path.exists(TestCRPIndividualDenormalization.output_path):
            os.remove(TestCRPIndividualDenormalization.output_path)   
        if os.path.exists(TestCRPDenormalizePac2Candidate.output_path):
            os.remove(TestCRPDenormalizePac2Candidate.output_path)      
        if os.path.exists(TestCRPDenormalizePac2Pac.output_path):
            os.remove(TestCRPDenormalizePac2Pac.output_path)    
            
        Contribution.objects.all().delete()    
            
        call_command('crp_denormalize', cycles='08', dataroot='dc_data/test_data') 
        call_command('loadcontributions', TestCRPIndividualDenormalization.output_path)
        call_command('loadcontributions', TestCRPDenormalizePac2Candidate.output_path)
        call_command('loadcontributions', TestCRPDenormalizePac2Pac.output_path) 
         
        self.assertEqual(30, Contribution.objects.all().count())
        

class TestCRPIndividualDenormalization(TestCase):
    output_path = 'dc_data/test_data/denormalized/denorm_indivs.08.csv'
    
    def test_command(self):
        
        if os.path.exists(self.output_path):
            os.remove(self.output_path)
        
        call_command('crp_denormalize_individuals', cycles='08', dataroot='dc_data/test_data')
        
        self.assertEqual(10, sum(1 for _ in open('dc_data/test_data/raw/crp/indivs08.csv', 'r')))
        self.assertEqual(11, sum(1 for _ in open(self.output_path, 'r')))

    def test_process_record(self):
        
        input_values = ["2000","0011161","f0000263005 ","VAN SYCKLE, LORRAINE E","C00040998","","","T2300","02/22/1999","200","","BANGOR","ME","04401","PB","15 ","C00040998","","F","VAN SYCKLE LM","99034391444","","","P/PAC"]
        input_record = dict(zip(FILE_TYPES['indivs'], input_values))
        
        record_processor = CRPDenormalizeIndividual.get_record_processor({}, {}, {})
        output_record = record_processor(input_record)

        self.assertEqual(set(model_fields('contribution.Contribution')), set(output_record.keys()))
        
    def test_process(self):
        
        input_rows = [["2000","0011161","f0000263005 ","VAN SYCKLE, LORRAINE E","C00040998","","","T2300","02/22/1999","200","","BANGOR","ME","04401","PB","15 ","C00040998","","F","VAN SYCKLE LM","99034391444","","","P/PAC"],
                      ["2000","0011162","f0000180392 ","MEADOR, F B JR","C00040998","","","T2300","02/16/1999","200","","PRNC FREDERCK","MD","20678","PB","15 ","C00040998","","M","BAYSIDE CHEVROLET BUICK","99034391444","","","P/PAC"],
                      ["2000","0011163","f0000180361 ","PATKIN, MURRAY","C00040998","","","T2300","02/22/1999","500","","WATERTOWN","MA","02472","PB","15 ","C00040998","","M","TOYOTA OF WATERTOWN","99034391444","","","P/PAC"],
                      ["2000","0011164","f0000082393 ","DELUCA, WILLIAM P III","C00040998","","","T2300","02/24/1999","1000","","BRADFORD","MA","01835","PB","15 ","C00040998","","M","BILL DELUCA CHEVY PONTIAC","99034391445","","","P/PAC"],
                      ["2000","0011165","f0000180362 ","BERGER, MATTHEW S","C00040998","","","T2300","02/12/1999","2000","","GRAND RAPIDS","MI","49512","PB","15 ","C00040998","","M","BERGER CHEVROLET INC","99034391445","","","P/PAC"]]
        input_records = [dict(zip(FILE_TYPES['indivs'], row)) for row in input_rows]
        output_records = list()
        record_processor = CRPDenormalizeIndividual.get_record_processor({}, {}, {})
        
        load_data(input_records, record_processor, output_records.append)
        
        self.assertEqual(5, len(output_records))
        


class TestCRPDenormalizePac2Candidate(TestCase):
    output_path = 'dc_data/test_data/denormalized/denorm_pac2cand.csv'
    
    def test_command(self):
        
        if os.path.exists(self.output_path):
            os.remove(self.output_path)
        
        call_command('crp_denormalize_pac2candidate', cycles='08', dataroot='dc_data/test_data')
        
        self.assertEqual(10, sum(1 for _ in open('dc_data/test_data/raw/crp/pacs08.csv', 'r')))
        self.assertEqual(11, sum(1 for _ in open(self.output_path, 'r')))
                

class TestCRPDenormalizePac2Pac(TestCase):
    output_path = 'dc_data/test_data/denormalized/denorm_pac2pac.csv'
    
    def test_command(self):
        
        if os.path.exists(self.output_path):
            os.remove(self.output_path)
        
        call_command('crp_denormalize_pac2pac', cycles='08', dataroot='dc_data/test_data')
        
        self.assertEqual(10, sum(1 for _ in open('dc_data/test_data/raw/crp/pac_other08.csv', 'r')))
        self.assertEqual(11, sum(1 for _ in open(self.output_path, 'r')))
        

class TestLoadContributions(TestCase):
        
    def test_command(self):
        Contribution.objects.all().delete()
        
        call_command('crp_denormalize_individuals', cycles='08', dataroot='dc_data/test_data')
        call_command('loadcontributions', 'dc_data/test_data/denormalized/denorm_indivs.08.csv')
        
        self.assertEqual(10, Contribution.objects.all().count())
        



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
            