

from decimal import Decimal
import os
from django.test import TestCase
from nose.plugins.skip import Skip, SkipTest
import shutil

from dcdata.contribution.models import Contribution
from dcdata.contribution.sources.crp import FILE_TYPES
from dcdata.loading import model_fields, LoaderEmitter
from dcdata.management.commands.crp_denormalize_individuals import \
    CRPDenormalizeIndividual
from dcdata.management.commands.loadearmarks import FIELDS as EARMARK_FIELDS, LoadTCSEarmarks
from dcdata.management.commands.loadcontributions import LoadContributions, \
    ContributionLoader, StringLengthFilter
#from dcdata.management.commands.nimsp_denormalize import NIMSPDenormalize
from dcdata.processor import load_data, chain_filters, compose_one2many,\
    SkipRecordException
from django.core.management import call_command
from django.db import connection
from saucebrush.filters import ConditionalFilter, YieldFilter, FieldModifier
from scripts.nimsp.common import CSV_SQL_MAPPING
from updates import edits, update
from dcdata.management.commands.crp_denormalize import load_candidates,\
    load_committees
from dcdata.utils.dryrub import FieldCountValidator, VerifiedCSVSource,\
    CSVFieldVerifier
from dcdata import processor
from saucebrush.sources import CSVSource
from scripts.nimsp.salt import DCIDFilter, SaltFilter
import sqlite3
import sys


dataroot = os.path.abspath(os.path.join(os.path.dirname(__file__), 'test_data'))

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

        input_row = ["2010","1087969","U00000034611","ROTHSCHILD, STANFORD  Z","C00420174",
                     "Rothschild Capital Management","","F2100",02/24/2010,47800,"","TOWSON","MD",
                     "21204","RP","15 ","C00420174","","M","ROTHSCHILD CAPITAL/CEO","10990384035","","","Name "]

        self.assertEqual(len(FILE_TYPES['indivs']), len(input_row))
        input_record = dict(zip(FILE_TYPES['indivs'], input_row))

        (output_record,) = processor(input_record)

        assert_record_contains(self, {'recipient_category': 'Z4100' }, output_record)



class TestNIMSPDenormalize(TestCase):
    original_salts_db_path = os.path.join(dataroot, 'denormalized/original_salts.db')
    salts_db_path = os.path.join(dataroot, 'denormalized/salts.db')
    output_paths = [os.path.join(dataroot, 'denormalized/nimsp_allocated_contributions.csv'),
                    os.path.join(dataroot, 'denormalized/nimsp_unallocated_contributions.csv')]

    def setUp(self):
        for path in self.output_paths + [self.salts_db_path]:
            if os.path.exists(path):
                os.remove(path)

        shutil.copy(self.original_salts_db_path, self.salts_db_path)


    def test_salting(self):
        raise SkipTest
        input_string = '"3327568","341.66","2006-11-07","MISC CONTRIBUTIONS $10000 AND UNDER","UNITEMIZED DONATIONS",\
                        "MISC CONTRIBUTIONS $100.00 AND UNDER","","","","","","","","","","","OR","","Z2400","0","0",\
                        "0",\N,"0","1825","PAC 483","2006",\N,\N,\N,\N,\N,\N,"I","PAC 483","130","OR"'
        source = CSVSource([input_string], [name for (name, _, _) in CSV_SQL_MAPPING])
        output = list()

        processor = NIMSPDenormalize.get_unallocated_record_processor(self.salts_db_path)

        load_data(source, processor, output.append)


        self.assertEqual(2, len(output))
        self.assertAlmostEqual(Decimal('341.66'), output[0]['amount'] + output[1]['amount'])


    def test_output_switch(self):
        raise SkipTest
        self.assertFalse(os.path.exists(self.output_paths[0]))
        self.assertFalse(os.path.exists(self.output_paths[1]))

        call_command('nimsp_denormalize', dataroot=dataroot, saltsdb=self.salts_db_path)

        self.assertTrue(os.path.exists(self.output_paths[0]))
        self.assertTrue(os.path.exists(self.output_paths[1]))

        os.remove(self.output_paths[1])
        self.assertFalse(os.path.exists(self.output_paths[1]))

        call_command('nimsp_denormalize', dataroot=dataroot, saltsdb=self.salts_db_path, output_types='unallocated')

        self.assertTrue(os.path.exists(self.output_paths[1]))

        os.remove(self.output_paths[0])
        os.remove(self.output_paths[1])
        self.assertFalse(os.path.exists(self.output_paths[0]))
        self.assertFalse(os.path.exists(self.output_paths[1]))

        call_command('nimsp_denormalize', dataroot=dataroot, saltsdb=self.salts_db_path, output_types='allocated')

        self.assertTrue(os.path.exists(self.output_paths[0]))
        self.assertFalse(os.path.exists(self.output_paths[1]))


    def test_command(self):
        raise SkipTest

        call_command('nimsp_denormalize', dataroot=dataroot, saltsdb=self.salts_db_path)

        self.assertEqual(9, sum(1 for _ in open(self.output_paths[0], 'r')))
        self.assertEqual(4, sum(1 for _ in open(self.output_paths[1], 'r')))

        Contribution.objects.all().delete()

        for path in self.output_paths:
            call_command('loadcontributions', path)

        self.assertEqual(11, Contribution.objects.all().count())


    def test_recipient_state(self):
        raise SkipTest
        self.test_command()

        self.assertEqual(7, Contribution.objects.filter(recipient_state='OR').count())
        self.assertEqual(2, Contribution.objects.filter(recipient_state='WA').count())

    def test_salt_filter(self):
        raise SkipTest

        connection = sqlite3.connect(self.salts_db_path)
        connection.cursor().execute('delete from salts where nimsp_id = 9999')
        connection.commit()
        connection.close()

        filter = SaltFilter(0, self.salts_db_path, DCIDFilter())

        r = {'contributionid': 9999,
            'amount': Decimal('1234.56'),
            'contributor_state': 'MI',
            'date': '2010-03-16'}

        output = list(filter.process_record(r))

        self.assertEqual(2, len(output))

    def test_contributor_type(self):
        raise SkipTest
        input_string = '"3327568","341.66","2006-11-07","Adams, Kent","Adams, Kent",\
                        "MISC CONTRIBUTIONS $100.00 AND UNDER","","","","Adams & Boswell","","","","","","","OR","","A1000","0","0",\
                        "0",\N,"0","1825","PAC 483","2006",\N,\N,\N,\N,\N,\N,"I","PAC 483","130","OR"'
        source = CSVSource([input_string], [name for (name, _, _) in CSV_SQL_MAPPING])
        output = list()

        processor = NIMSPDenormalize.get_allocated_record_processor()

        load_data(source, processor, output.append)

        assert_record_contains(self, {'contributor_type': 'individual', 'organization_name': "Adams & Boswell"}, output[0])

        input_string = '"3327568","341.66","2006-11-07","Kent Adams","Kent Adams",\
                        "MISC CONTRIBUTIONS $100.00 AND UNDER","","","","","","","","","","","OR","","A1000","0","0",\
                        "0",\N,"0","1825","PAC 483","2006",\N,\N,\N,\N,\N,\N,"I","PAC 483","130","OR"'
        source = CSVSource([input_string], [name for (name, _, _) in CSV_SQL_MAPPING])
        output = list()

        processor = NIMSPDenormalize.get_allocated_record_processor()

        load_data(source, processor, output.append)

        assert_record_contains(self, {'contributor_type': 'committee', 'organization_name': "Kent Adams"}, output[0])


class TestCRPDenormalizeAll(TestCase):

    def test_denormalize_and_load(self):
        if os.path.exists(TestCRPIndividualDenormalization.output_path):
            os.remove(TestCRPIndividualDenormalization.output_path)
        if os.path.exists(TestCRPDenormalizePac2Candidate.output_path):
            os.remove(TestCRPDenormalizePac2Candidate.output_path)
        if os.path.exists(TestCRPDenormalizePac2Pac.output_path):
            os.remove(TestCRPDenormalizePac2Pac.output_path)

        call_command('crp_denormalize', cycles='08', dataroot=dataroot)
        call_command('loadcontributions', TestCRPIndividualDenormalization.output_path)
        call_command('loadcontributions', TestCRPDenormalizePac2Candidate.output_path)
        call_command('loadcontributions', TestCRPDenormalizePac2Pac.output_path)

        self.assertEqual(30, Contribution.objects.all().count())


class TestCRPIndividualDenormalization(TestCase):
    output_path = os.path.join(dataroot, 'denormalized/denorm_indivs.08.txt')

    def test_command(self):

        if os.path.exists(self.output_path):
            os.remove(self.output_path)

        call_command('crp_denormalize_individuals', cycles='08', dataroot=dataroot)

        input_path = os.path.join(dataroot, 'raw/crp/indivs08.txt')
        self.assertEqual(10, sum(1 for _ in open(input_path, 'r')))
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
    output_path = os.path.join(dataroot, 'denormalized/denorm_pac2cand.txt')

    def test_command(self):

        if os.path.exists(self.output_path):
            os.remove(self.output_path)

        call_command('crp_denormalize_pac2candidate', cycles='08', dataroot=dataroot)

        input_path = os.path.join(dataroot, 'raw/crp/pacs08.txt')
        self.assertEqual(10, sum(1 for _ in open(input_path, 'r')))
        self.assertEqual(11, sum(1 for _ in open(self.output_path, 'r')))


class TestCRPDenormalizePac2Pac(TestCase):
    output_path = os.path.join(dataroot, 'denormalized/denorm_pac2pac.txt')

    def test_command(self):

        if os.path.exists(self.output_path):
            os.remove(self.output_path)

        call_command('crp_denormalize_pac2pac', cycles='08', dataroot=dataroot)

        input_path = os.path.join(dataroot, 'raw/crp/pac_other08.txt')
        self.assertEqual(10, sum(1 for _ in open(input_path, 'r')))
        self.assertEqual(11, sum(1 for _ in open(self.output_path, 'r')))


class TestLoadContributions(TestCase):


    def test_command(self):
        call_command('crp_denormalize_individuals', cycles='08', dataroot=dataroot)
        call_command('loadcontributions', os.path.join(dataroot, 'denormalized/denorm_indivs.08.txt'))

        self.assertEqual(10, Contribution.objects.all().count())

    def test_skip(self):
        call_command('crp_denormalize_individuals', cycles='08', dataroot=dataroot)
        call_command('loadcontributions', os.path.join(dataroot, 'denormalized/denorm_indivs.08.txt'), skip='3')

        self.assertEqual(7, Contribution.objects.all().count())

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

    def test_bad_value(self):
        # the second record has an out-of-range date
        input_rows = [',,2006,urn:nimsp:transaction,4cd6577ede2bfed859e21c10f9647d3f,,,False,8.5,2006-11-07,|BOTTGER, ANTHONY|,,,,SEWER WORKER,CITY OF PORTLAND,,19814 NE HASSALO,PORTLAND,OR,97230,X3000,,CITY OF PORTLAND,,,,,,PAC 483,1825,,I,committee,OR,,,PAC 483,1825,,I,,,,,',
                      ',,1998,urn:nimsp:transaction,227059e3c32af276f5b37642922e415c,,,False,200,0922-09-08,|TRICK, BILL|,,,,,,,BOX 2730,TUSCALOOSA,AL,35403,B1500,,,,,,,,|BENTLEY, ROBERT J|,3188,,R,politician,AL,,,,,,,G,AL-21,state:upper,,L',
                      ',,2006,urn:nimsp:transaction,dd0af37dca3bf26b2aa602e4d8756c19,,,False,8,2006-11-07,|BRAKE, PATRICK|,,,,UTILITY WORKER,CITY OF PORTLAND,,73728 SOLD RD,RAINIER,OR,97048,X3000,,CITY OF PORTLAND,,,,,,PAC 483,1825,,I,committee,OR,,,PAC 483,1825,,I,,,,,']

        loader = ContributionLoader(
                source='unittest',
                description='unittest',
                imported_by='unittest'
            )
        source = CSVSource(input_rows, model_fields('contribution.Contribution'))
        processor = LoadContributions.get_record_processor(loader.import_session)
        output = LoaderEmitter(loader).process_record

        sys.stderr.write("Error expected:\n")

        load_data(source, processor, output)

        self.assertEqual(2, Contribution.objects.count())

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

    def test_string_length(self):
        original = {'contributor_zipcode': '123456',\
                    'contributor_employer': '1111111111222222222233333333334444444444555555555566666666667777777777',\
                    'contributor_occupation': 'too short'}

        filter = StringLengthFilter(Contribution)

        result = filter.process_record(original)

        self.assertEqual('12345', result['contributor_zipcode'])
        self.assertEqual('1111111111222222222233333333334444444444555555555566666666667777', result['contributor_employer'])
        self.assertEqual('too short', result['contributor_occupation'])


class TestEarmarks(TestCase):
    csv2008 = [
        '1214,38777000,6305310,38041000,38200000,,"Arts in Education Program (VSA Arts and John F. Kennedy Center for the Performing Arts) for model arts education and other activities",,,"UNK","Labor-HHS-Education","Department of Education","Innovation and Improvement",,"Abercrombie","D","HI",,"Bingaman; Cochran; Kennedy","D; R; D","NM; MS; MA",,,,',
        '1,300000,,425000,414000,,"Boys & Girls Club of Hawaii, Honolulu, HI for a multi-media center, which may include equipment","Honolulu",,"HI","Labor-HHS-Education","Department of Education","Fund for the Improvement of Education",,"Abercrombie","D","HI",,,,,,,,',
        '1,,1500000,1500000,1476000,,"Cellular Bioengineering, Inc., Continue development of polymeric hydrogels for radiation decontamination","Honolulu",,"HI","Energy & Water","Department of Energy","Defense Environmental Cleanup",,"Abercrombie","D","HI",,"Inouye","D","HI",,,,'
    ]

    csv2009 = [
        ',,,,2000000,,"101st Airborne Injury Prevention & Performance Enhancement Research Initiative",,,"KY","Defense","RDTE","Army",,,,,,"Alexander, Lamar; Corker","R; R","TN; TN",,,,',
        ',,,,10000000,,"11th Air Force Consolidated Command Center",,,"AK","Defense","Operation and Maintenance","Air Force",,,,,,"Stevens","R","AK",,,,',
        ',,,,3200000,,"11th Air Force Critical Communications Infrastructure",,,"AK","Defense","Operation and Maintenance","Air Force",,,,,,"Stevens","R","AK",,,,'
    ]

    csv2010 = [
        ',,3000000,,3000000,,"101st Airborne/Air Assault Injury Prevention and Performance Enhancement Initiative","Fort Campbell",,"KY","Defense","Research, Development, Test & Evaluation","Army",,,,,,"Corker; Specter","R; D","TN; PA",,,"University of Pittsburgh",',
        ',,500000,,500000,,"10th Avenue South Corridor Extension, Waverly, IA","Waverly",,"IA","Transportation-Housing and Urban Development","Federal Highway Administration","Surface Transportation Priorities",,"Braley","D","IA",,"Grassley; Harkin","R; D","IA; IA",,,,',
        ',500000,,,500000,,"10th St. Connector-To extend 10th Street from Dickinson Avenue to Stantonsburg Road, Greenville, NC","Greenville",,"NC","Transportation-Housing and Urban Development","Federal Highway Administration","Transportation & Community & System Preservation",,"Jones, Walter","R","NC",,"Burr","R","NC",,,,'
    ]
    
    def test_load_earmarks(self):
        source = VerifiedCSVSource(self.csv2008, EARMARK_FIELDS)
        processor = LoadTCSEarmarks.get_record_processor(2008, None)
        output = list()
        
        load_data(source, processor, output.append)
        
        self.assertEqual(3, len(output))


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

