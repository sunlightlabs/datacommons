

from decimal import Decimal
import os
from unittest import TestCase

from dcdata.contribution.models import Contribution
from dcdata.contribution.sources.crp import FILE_TYPES
from dcdata.loading import model_fields, LoaderEmitter
from dcdata.management.commands.crp_denormalize_individuals import \
    CRPDenormalizeIndividual
from dcdata.management.commands.loadcontributions import LoadContributions, \
    ContributionLoader
from dcdata.management.commands.nimsp_denormalize import NIMSPDenormalize
from dcdata.processor import load_data, chain_filters, compose_one2many,\
    SkipRecordException
from django.core.management import call_command
from django.db import connection
from saucebrush.filters import ConditionalFilter, YieldFilter, FieldModifier
from scripts.nimsp.common import CSV_SQL_MAPPING
from updates import edits, update
from dcdata.management.commands.crp_denormalize import load_candidates,\
    load_committees
import csv
from dcdata.utils.dryrub import FieldCountValidator, VerifiedCSVSource,\
    CSVFieldVerifier
from dcdata import processor
from saucebrush.sources import CSVSource


dataroot = 'dc_data/test_data'

def assert_record_contains(tester, expected, actual):
    for (name, value) in expected.iteritems():
        tester.assertEqual(value, actual[name])



class TestRecipientFilter(TestCase):
    
    def test(self):
        processor = CRPDenormalizeIndividual.get_record_processor((),
                                                                  load_candidates(dataroot),
                                                                  load_committees(dataroot))
        
        input_row = ["2008","0000011","i3003166469 ","ADAMS, KENT","N00005985","Adams & Boswell","","K1000",
                        "12/11/2006","1000","PO  12523","BEAUMONT","TX","77726","RN","15 ","C00257402","","M",
                        "ADAMS & BOSWELL/ATTORNEY","27930036083","Attorney","Adams & Boswell","Rept "]
        self.assertEqual(len(FILE_TYPES['indivs']), len(input_row))
        input_record = dict(zip(FILE_TYPES['indivs'], input_row))
        
        (output_record,) = processor(input_record)
        
        assert_record_contains(self, {'recipient_name': 'Henry Bonilla (R)',
                                      'recipient_party': 'R',
                                      'recipient_type': 'politician',
                                      'recipient_ext_id': 'N00005985',
                                      'seat_status': ' ',
                                      'seat_result': None,
                                      'recipient_state': 'TX',
                                      'seat': 'federal:house',
                                      'district': 'TX-23'},
                                       output_record)
        
        input_row = ["2008","0000880","j1001101935 ","AMBERSON, RAY","C00030718","","","F4200",
                     "12/08/2006","300","PO  6","ALBERTVILLE","AL","35950","PB","15 ","C00030718",
                     "","M","HENDERSON & SPURLIN REAL ESTAT/REAL","27930132133","Real Estate Broker",
                     "Henderson & Spurlin Real Estat","P/PAC"]
        self.assertEqual(len(FILE_TYPES['indivs']), len(input_row))
        input_record = dict(zip(FILE_TYPES['indivs'], input_row))
        
        (output_record,) = processor(input_record)

        assert_record_contains(self, {'recipient_name': 'National Assn of Realtors',
                                      'recipient_party': '',
                                      'recipient_type': 'committee',
                                      'recipient_ext_id': 'C00030718',
                                      'seat_result': None},
                                       output_record)



class TestNIMSPDenormalize(TestCase):
    salts_db_path = 'dc_data/test_data/denormalized/salts.db'
    output_paths = ['dc_data/test_data/denormalized/nimsp_allocated_contributions.csv', 
                    'dc_data/test_data/denormalized/nimsp_unallocated_contributions.csv']
    
    def test_dump(self):
        self.fail("Not running unit test because of temporary firewall issues with MySQL on Smokehouse.")
        
        partial_path = '/tmp/test_nimsp_dump.csv'
        
        if os.path.exists(partial_path):
            os.remove(partial_path)
            
        call_command('nimsp_dump', outfile=partial_path, number=10)
        
        self.assertEqual(10, sum(1 for _ in open(partial_path, 'r')))    
        
    
    def test_salting(self):
        input_string = '"3429235","341.66","2006-11-07","MISC CONTRIBUTIONS $10000 AND UNDER","UNITEMIZED DONATIONS",\
                        "MISC CONTRIBUTIONS $100.00 AND UNDER","","","","","","","","","","","OR","","Z2400","0","0",\
                        "0",\N,"0","1825","PAC 483","2006",\N,\N,\N,\N,\N,\N,"I","PAC 483","130","OR"'
        source = CSVSource([input_string], [name for (name, _, _) in CSV_SQL_MAPPING])
        output = list()
    
        processor = NIMSPDenormalize.get_unallocated_record_processor(self.salts_db_path)

        load_data(source, processor, output.append)
                    
        self.assertEqual(2, len(output))
        self.assertAlmostEqual(Decimal('341.66'), output[0]['amount'] + output[1]['amount'])
    
    def test_command(self):
        for path in self.output_paths:
            if os.path.exists(path):
                os.remove(path)     

        call_command('nimsp_denormalize', dataroot=dataroot, saltsdb=self.salts_db_path)
        
        self.assertEqual(9, sum(1 for _ in open(self.output_paths[0], 'r')))
        self.assertEqual(4, sum(1 for _ in open(self.output_paths[1], 'r')))
        
        Contribution.objects.all().delete()
        
        for path in self.output_paths:
            call_command('loadcontributions', path)
        
        self.assertEqual(11, Contribution.objects.all().count())
    
    
    def test_recipient_state(self):
        self.test_command()
        
        self.assertEqual(7, Contribution.objects.filter(recipient_state='OR').count())
        self.assertEqual(2, Contribution.objects.filter(recipient_state='WA').count())
        

class TestCRPDenormalizeAll(TestCase):
    
    def test_denormalize_and_load(self):
        if os.path.exists(TestCRPIndividualDenormalization.output_path):
            os.remove(TestCRPIndividualDenormalization.output_path)   
        if os.path.exists(TestCRPDenormalizePac2Candidate.output_path):
            os.remove(TestCRPDenormalizePac2Candidate.output_path)      
        if os.path.exists(TestCRPDenormalizePac2Pac.output_path):
            os.remove(TestCRPDenormalizePac2Pac.output_path)    
            
        Contribution.objects.all().delete()    
            
        call_command('crp_denormalize', cycles='08', dataroot=dataroot) 
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
        self.assert_row_succeeds(input_values)
        
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
        
        
    def assert_row_succeeds(self, input_values):
        self.assertEqual(len(FILE_TYPES['indivs']), len(input_values))
        input_record = dict(zip(FILE_TYPES['indivs'], input_values))
        
        record_processor = CRPDenormalizeIndividual.get_record_processor({}, {}, {})
        output_records = record_processor(input_record)
        
        self.assertEqual(1, len(output_records))
        self.assertEqual(set(model_fields('contribution.Contribution')), set(output_records[0].keys()))

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
        
            
    def test_decimal_amounts(self):
        """ See ticket #177. """
        
        input_row = ["2000","0011161","f0000263005 ","VAN SYCKLE, LORRAINE E","C00040998","","","T2300","02/22/1999","123.45","","BANGOR","ME","04401","PB","15 ","C00040998","","F","VAN SYCKLE LM","99034391444","","","P/PAC"]
        input_record = dict(zip(FILE_TYPES['indivs'], input_row))
        denormalized_records = list()
        denormalizer = CRPDenormalizeIndividual.get_record_processor({}, {}, {})
        
        load_data([input_record], denormalizer, denormalized_records.append)
        
        self.assertEqual(1, len(denormalized_records))
        self.assertEqual(u'123.45', denormalized_records[0]['amount'])
        
        Contribution.objects.all().delete()
        
        loader = ContributionLoader(
            source='unittest',
            description='unittest',
            imported_by='unittest'
        )
        output_func = LoaderEmitter(loader).process_record
        processor = LoadContributions.get_record_processor(loader.import_session)
        
        load_data(denormalized_records, processor, output_func)
        
        self.assertEqual(1, Contribution.objects.all().count())
        self.assertEqual(Decimal('123.45'), Contribution.objects.all()[0].amount)
        
        
class TestProcessor(TestCase):
    
    def test_chain(self):
        f = compose_one2many()
        
        self.assertEqual([5], list(f(5)))
        self.assertEqual(['foo'], list(f('foo')))
        
        f = compose_one2many(lambda x: [x * 2])
        
        self.assertEqual([4], list(f(2)))
        self.assertEqual(['foofoo'], list(f('foo')))
        
        f = compose_one2many(lambda x: [x, x])
        
        self.assertEqual([2, 2], list(f(2)))
        self.assertEqual(['foo', 'foo'], list(f('foo')))
        
        f = compose_one2many(lambda x: [x, x + 3],
                          lambda x: [x, x * 3])
        
        self.assertEqual([1, 3, 4, 12], list(f(1)))
        
        f = compose_one2many(lambda x: [x + 'a', x + 'b'],
                          lambda x: [x + 'c'],
                          lambda x: [x + 'd', x + 'e', x + 'f'])
        
        self.assertEqual(['acd', 'ace', 'acf', 'bcd', 'bce', 'bcf'], list(f('')))

    def test_filters(self):
        class Cube(YieldFilter):
            def process_record(self, r):
                yield r
                r2 = r.copy()
                r2['value'] *= r['value']
                yield r2
                r3 = r2.copy()
                r3['value'] *= r['value']
                yield r3
                
        class Evens(ConditionalFilter):
            def test_record(self, record):
                return record['value'] % 2 == 0
            
        f = chain_filters(Cube(),
                          FieldModifier(('value'), abs),
                          Evens())
        
        self.assertEqual([{'value':0}] * 3, f({'value':0}))
        self.assertEqual([], f({'value':1}))
        self.assertEqual([{'value': 2}, {'value': 4}, {'value': 8}], f({'value':2}))
        self.assertEqual([{'value': 2}, {'value': 4}, {'value': 8}], f({'value':-2}))
        
    def test_field_count_validator(self):
        validator = FieldCountValidator(2)
        
        single = {'a': 1}
        double = {'a': 1, 'b': 2}
        triple = {'a': 1, 'b': 2, 'c': 3}
        
        self.assertRaises(SkipRecordException, validator.process_record, [single])
        self.assertEqual(double, validator.process_record(double))
        self.assertRaises(SkipRecordException, validator.process_record, [triple])
        
        processor.TERMINATE_ON_ERROR = False
        
        output = list()
        load_data([single, double, triple, double], chain_filters(validator), output.append)
        self.assertEqual([double, double], output)
        
    def test_verified_csv_source(self):
        processor.TERMINATE_ON_ERROR = False

        inputs = ["1,2", "1,2,3", "1,2,3,4"]
        source = VerifiedCSVSource(inputs, ['a', 'b', 'c'])
        f = chain_filters(CSVFieldVerifier())
        output = list()
        
        load_data(source, f, output.append)
        self.assertEqual([{'a': '1', 'b': '2', 'c': '3'}], output)
        


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
            