from cStringIO import StringIO
from dcdata import processor
from dcdata.contribution.models import Contribution
from dcdata.contribution.sources.crp import FILE_TYPES
from dcdata.earmarks.models import Earmark, Member
from dcdata.loading import model_fields, LoaderEmitter, SkipRecordException
from dcdata.management.commands.crp_denormalize import load_candidates, \
    load_committees
from dcdata.management.commands.crp_denormalize_individuals import \
    CRPDenormalizeIndividual
from dcdata.management.commands.loadcontributions import LoadContributions, \
    ContributionLoader, StringLengthFilter
from dcdata.management.commands.loadearmarks import FIELDS as EARMARK_FIELDS, \
    LoadTCSEarmarks, save_earmark, _normalize_locations, split_and_transpose
from dcdata.models import Import
from dcdata.processor import load_data, chain_filters, compose_one2many, \
    SkipRecordException
from dcdata.scripts.usaspending.converter import USASpendingDenormalizer
from dcdata.scripts.usaspending.loader import Loader
from dcdata.utils.dryrub import FieldCountValidator, VerifiedCSVSource, \
    CSVFieldVerifier
from decimal import Decimal
from django.core.management import call_command
from django.db import connections
from django.test import TestCase
from nose.plugins.attrib import attr
from nose.plugins.skip import Skip, SkipTest
from saucebrush.filters import ConditionalFilter, YieldFilter, FieldModifier
from saucebrush.sources import CSVSource
from scripts.nimsp.common import CSV_SQL_MAPPING
from scripts.nimsp.salt import DCIDFilter, SaltFilter
from tempfile import NamedTemporaryFile
from updates import edits, update
import os, os.path, re, shutil, sqlite3, sys

from dcdata.management.commands.nimsp_denormalize import NIMSPDenormalize


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


    @attr('mysql')
    def test_salting(self):
        input_string = '"3327568","341.66","2006-11-07","MISC CONTRIBUTIONS $10000 AND UNDER","UNITEMIZED DONATIONS",\
                        "MISC CONTRIBUTIONS $100.00 AND UNDER","","","","","","","","","","","OR","","Z2400","0","0",\
                        "0",\N,"0","1825","PAC 483","2006",\N,\N,\N,\N,\N,\N,"I","PAC 483","130","OR"'
        source = CSVSource([input_string], [name for (name, _, _) in CSV_SQL_MAPPING])
        output = list()

        processor = NIMSPDenormalize.get_unallocated_record_processor(self.salts_db_path)

        load_data(source, processor, output.append)

        self.assertEqual(2, len(output))
        self.assertAlmostEqual(Decimal('341.66'), output[0]['amount'] + output[1]['amount'])


    @attr('mysql')
    def test_output_switch(self):
        self.assertFalse(os.path.exists(self.output_paths[0]))
        self.assertFalse(os.path.exists(self.output_paths[1]))

        call_command('nimsp_denormalize', dataroot=dataroot, saltsdb=self.salts_db_path, dest_dir=os.path.join(dataroot, 'denormalized'))

        self.assertTrue(os.path.exists(self.output_paths[0]))
        self.assertTrue(os.path.exists(self.output_paths[1]))

        os.remove(self.output_paths[1])
        self.assertFalse(os.path.exists(self.output_paths[1]))

        call_command('nimsp_denormalize', dataroot=dataroot, saltsdb=self.salts_db_path, output_types='unallocated', dest_dir=os.path.join(dataroot, 'denormalized'))

        self.assertTrue(os.path.exists(self.output_paths[1]))

        os.remove(self.output_paths[0])
        os.remove(self.output_paths[1])
        self.assertFalse(os.path.exists(self.output_paths[0]))
        self.assertFalse(os.path.exists(self.output_paths[1]))

        call_command('nimsp_denormalize', dataroot=dataroot, saltsdb=self.salts_db_path, output_types='allocated', dest_dir=os.path.join(dataroot, 'denormalized'))

        self.assertTrue(os.path.exists(self.output_paths[0]))
        self.assertFalse(os.path.exists(self.output_paths[1]))


    @attr('mysql')
    def test_command(self):
        call_command('nimsp_denormalize', dataroot=dataroot, saltsdb=self.salts_db_path, dest_dir=os.path.join(dataroot, 'denormalized'))

        self.assertEqual(9, sum(1 for _ in open(self.output_paths[0], 'r')))
        self.assertEqual(4, sum(1 for _ in open(self.output_paths[1], 'r')))

        Contribution.objects.all().delete()

        for path in self.output_paths:
            call_command('loadcontributions', path)

        self.assertEqual(11, Contribution.objects.all().count())


    @attr('mysql')
    def test_recipient_state(self):
        self.test_command()

        self.assertEqual(7, Contribution.objects.filter(recipient_state='OR').count())
        self.assertEqual(2, Contribution.objects.filter(recipient_state='WA').count())

    @attr('mysql')
    def test_salt_filter(self):
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

    @attr('mysql')
    def test_contributor_type(self):
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

        # Prevent this test from spewing the expected error to the command line
        old_stderr = sys.stderr
        sys.stderr = mystderr = StringIO()
        load_data(source, processor, output)
        sys.stderr = old_stderr

        self.assertTrue(mystderr.getvalue())
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

        # prevent unwanted console output
        stderr_old = sys.stderr
        sys.stderr = mystderr = StringIO()

        load_data([single, double, triple, double], chain_filters(validator), output.append)

        sys.stderr = stderr_old

        self.assertTrue(mystderr.getvalue())
        self.assertEqual([double, double], output)

    def test_verified_csv_source(self):
        processor.TERMINATE_ON_ERROR = False

        inputs = ["1,2", "1,2,3", "1,2,3,4"]
        source = VerifiedCSVSource(inputs, ['a', 'b', 'c'])
        f = chain_filters(CSVFieldVerifier())
        output = list()

        # prevent unwanted console output
        stderr_old = sys.stderr
        sys.stderr = mystderr = StringIO()

        load_data(source, f, output.append)

        sys.stderr = stderr_old

        self.assertTrue(mystderr.getvalue())
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
    
    def test_raw_fields(self):
        source = VerifiedCSVSource(self.csv2008[0:1], EARMARK_FIELDS)
        processor = LoadTCSEarmarks.get_record_processor(0, None)
        output = list()
        
        load_data(source, processor, output.append)
        
        self.assertEqual(1, len(output))
        self.assertEqual("Abercrombie", output[0]['house_members'])
        self.assertEqual("D", output[0]['house_parties'])
        self.assertEqual("HI", output[0]['house_states'])
        self.assertEqual("", output[0]['house_districts'])
        self.assertEqual("Bingaman; Cochran; Kennedy", output[0]['senate_members'])
        self.assertEqual("D; R; D", output[0]['senate_parties'])
        self.assertEqual("NM; MS; MA", output[0]['senate_states'])
        
    
    def test_process_earmarks(self):
        source = VerifiedCSVSource(self.csv2008 + self.csv2009 + self.csv2010, EARMARK_FIELDS)
        processor = LoadTCSEarmarks.get_record_processor(0, None)
        output = list()
        
        load_data(source, processor, output.append)
        
        self.assertEqual(9, len(output))
        
    def test_save_earmarks(self):
        Earmark.objects.all().delete()
        Member.objects.all().delete()
        import_ref = Import.objects.create()
        
        source = VerifiedCSVSource(self.csv2008 + self.csv2009 + self.csv2010, EARMARK_FIELDS)
        processor = LoadTCSEarmarks.get_record_processor(0, import_ref)
        
        load_data(source, processor, save_earmark)
        
        self.assertEqual(9, Earmark.objects.count())
        self.assertEqual(18, Member.objects.count())

    def test_choice_maps(self):
        variants = [
            ',,,,10000000,,"11th Air Force Consolidated Command Center",,,"AK","Defense","Operation and Maintenance","Air Force",,,,,,"Stevens","R","AK",President-Solo,Undisclosed,,',
            ',,,,10000000,,"11th Air Force Consolidated Command Center",,,"AK","Defense","Operation and Maintenance","Air Force",,,,,,"Stevens","R","AK",President-Solo & Und.,Undisclosed (President),,',
            ',,,,10000000,,"11th Air Force Consolidated Command Center",,,"AK","Defense","Operation and Maintenance","Air Force",,,,,,"Stevens","R","AK",President and Member(s),O & M-Disclosed,,',                        
            ',,,,10000000,,"11th Air Force Consolidated Command Center",,,"AK","Defense","Operation and Maintenance","Air Force",,,,,,"Stevens","R","AK",Judiciary,O & M-Undisclosed,,',                        
            ',,,,10000000,,"11th Air Force Consolidated Command Center",,,"AK","Defense","Operation and Maintenance","Air Force",,,,,,"Stevens","R","AK",something wrong,Something else entirely,,',                        
        ]

        Earmark.objects.all().delete()
        Member.objects.all().delete()
        import_ref = Import.objects.create()
        
        source = VerifiedCSVSource(variants, EARMARK_FIELDS)
        processor = LoadTCSEarmarks.get_record_processor(0, import_ref)
        load_data(source, processor, save_earmark)

        self.assertEqual(5, Earmark.objects.count())
        
        self.assertEqual(1, Earmark.objects.filter(undisclosed='u').count())
        self.assertEqual(1, Earmark.objects.filter(undisclosed='p').count())
        self.assertEqual(1, Earmark.objects.filter(undisclosed='o').count())
        self.assertEqual(1, Earmark.objects.filter(undisclosed='m').count())
        self.assertEqual(1, Earmark.objects.filter(undisclosed='').count())
        
        self.assertEqual(1, Earmark.objects.filter(presidential='p').count())
        self.assertEqual(1, Earmark.objects.filter(presidential='u').count())
        self.assertEqual(1, Earmark.objects.filter(presidential='m').count())
        self.assertEqual(1, Earmark.objects.filter(presidential='j').count())
        self.assertEqual(1, Earmark.objects.filter(presidential='').count())


    def test_locations(self):
        r = _normalize_locations("", "")
        self.assertEqual([], r)
        
        r = _normalize_locations("Portland", "")
        self.assertEqual(1, len(r))
        self.assertEqual(("Portland", ""), (r[0].city, r[0].state))

        r = _normalize_locations("", "OR")
        self.assertEqual(1, len(r))
        self.assertEqual(("","OR"), (r[0].city, r[0].state))
        
        r = _normalize_locations("Portland", "OR")
        self.assertEqual(1, len(r))
        self.assertEqual(("Portland", "OR"), (r[0].city, r[0].state))
        
        r = _normalize_locations("Portland; Seattle", "OR; WA")
        self.assertEqual(2, len(r))
        self.assertEqual(("Portland", "OR"), (r[0].city, r[0].state))
        self.assertEqual(("Seattle", "WA"), (r[1].city, r[1].state))
        
        r = _normalize_locations("Portland; Corvallis", "OR")
        self.assertEqual(2, len(r))
        self.assertEqual(("Portland", "OR"), (r[0].city, r[0].state))
        self.assertEqual(("Corvallis", "OR"), (r[1].city, r[1].state))
        
        r = _normalize_locations("", "OR; WA")
        self.assertEqual(2, len(r))
        self.assertEqual(("", "OR"), (r[0].city, r[0].state))
        self.assertEqual(("", "WA"), (r[1].city, r[1].state))

        r = _normalize_locations("Portland", "OR; WA")
        self.assertEqual(3, len(r))
        self.assertEqual(("Portland", ""), (r[0].city, r[0].state))
        self.assertEqual(("", "OR"), (r[1].city, r[1].state))
        self.assertEqual(("", "WA"), (r[2].city, r[2].state))


    def test_split_and_transpose(self):
        s = split_and_transpose(';')
        self.assertEqual([], s)
        
        s = split_and_transpose(';', 'a; b; c')
        self.assertEqual([('a',), ('b',), ('c',)], s)
        
        s = split_and_transpose(';', 'a; b; c', '1; 2; 3')
        self.assertEqual([('a', '1'), ('b', '2'), ('c', '3')], s)
        
        s = split_and_transpose(';', 'a; b', '1')
        self.assertEqual([('a', ''), ('b', '')], s)
        
        s = split_and_transpose(';', 'a; b', '1')
        self.assertEqual([('a', ''), ('b', '')], s)   
        
        s = split_and_transpose(';', 'a; b', '1', 'x; y; z')
        self.assertEqual([('a', '', ''), ('b', '', '')], s)  
        
        s = split_and_transpose(';', 'a; b', '1', 'x; y')
        self.assertEqual([('a', '', 'x'), ('b', '', 'y')], s)  
        

    def test_filters(self):
        csv = [
               '293,1500000,15000000,,1200000,,"Space Situational Awareness","College Station",,"TX","Defense","RDTE","Air Force","Advanced Spacecraft Technology","Edwards;","D","TX",,"Committee Initiative","N/A","N/A",,,"Texas A&M University",'
        ]
        
        source = VerifiedCSVSource(csv, EARMARK_FIELDS)
        processor = LoadTCSEarmarks.get_record_processor(0, None)
        output = list()
        
        load_data(source, processor, output.append)
        
        self.assertEqual(1, len(output))
        self.assertEqual(2, len(output[0]['members']))
        self.assertEqual('', output[0]['members'][1].party)
        self.assertEqual('', output[0]['members'][1].state)

    def test_recipients(self):
        csv = [
            '1214,38777000,6305310,38041000,38200000,,"Arts in Education Program (VSA Arts and John F. Kennedy Center for the Performing Arts) for model arts education and other activities",,,"UNK","Labor-HHS-Education","Department of Education","Innovation and Improvement",,"Abercrombie","D","HI",,"Bingaman; Cochran; Kennedy","D; R; D","NM; MS; MA",,,,',
            '1,300000,,425000,414000,,"Boys & Girls Club of Hawaii, Honolulu, HI for a multi-media center, which may include equipment","Honolulu",,"HI","Labor-HHS-Education","Department of Education","Fund for the Improvement of Education",,"Abercrombie","D","HI",,,,,,,"JC Penny",',
            '1,,1500000,1500000,1476000,,"Cellular Bioengineering, Inc., Continue development of polymeric hydrogels for radiation decontamination","Honolulu",,"HI","Energy & Water","Department of Energy","Defense Environmental Cleanup",,"Abercrombie","D","HI",,"Inouye","D","HI",,,"JC Penny; Macys;",'
        ]

        source = VerifiedCSVSource(csv, EARMARK_FIELDS)
        processor = LoadTCSEarmarks.get_record_processor(0, None)
        output = list()
        
        load_data(source, processor, output.append)
        
        self.assertEqual(3, len(output))
        (no_recip, one_recip, two_recips) = output
        self.assertEqual([], no_recip['recipients'])
        self.assertEqual('JC Penny', one_recip['recipients'][0].raw_recipient)
        self.assertEqual('JC Penny', two_recips['recipients'][0].raw_recipient)
        self.assertEqual('Macys', two_recips['recipients'][1].raw_recipient)
        
        
        
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
        self.cursor = connections['default'].cursor()

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
        new_table_cursor = connections['default'].cursor()
        updated_table_cursor = connections['default'].cursor()

        new_table_cursor.execute("select * from new_table order by id")
        updated_table_cursor.execute("select * from old_table order by id")

        for (new_row, updated_row) in map(None, new_table_cursor, updated_table_cursor):
            self.assertEqual(new_row, updated_row)


class TestConverter(TestCase):

    def test_prepare_grants_file(self):
        grants_file = NamedTemporaryFile('w')
        contracts_file = NamedTemporaryFile('w')

        out_dir = os.path.dirname(grants_file.name)

        USASpendingDenormalizer().parse_directory(os.path.join(os.path.dirname(__file__), 'test_data/usaspending'), out_dir, grants_file.name, contracts_file.name)

        self.assert_file_contents_eq('''
"c9b7090891d057c1336d6ae5f902243d","active","201010041","94.016","SAI NOT AVAILABLE","Hope for the Aged Inc.","06593","Bayaman","021","00956","12","A","9577","10SCAPR001","0","282687","49576","332263","2010-09-07","2010-09-30","2013-09-29","04","2",NULL,NULL,"7206593","Puerto Rico","Bayamon","00956","98  ","Senior Companion Program","Corporation for National and Community Service","Senior Companion Program","146240820","8 ","95","2728","000","Calle Duende 2 G1","Lomas Verdes",NULL,NULL,NULL,"2010","PR","n","g","ZZ","ot","N",NULL,"10SCAPR001020100907","PR"
"8a9788a5623095aabcb2d34fe57a4f67","active","201010041","94.006","SAI NOT AVAILABLE","Mississippi Institutions of Higher Learning","36000","Jackson","049","392116453","25","A","9577","10EDHMS002","0","160000",NULL,"160000","2010-09-29","2010-09-29","2011-07-31","04","2",NULL,NULL,"00*****","Mississippi","Hinds","392116453","00  ","AmeriCorps","Corporation for National and Community Service","Education Awards Program","023659365","8 ","95","2728","000","MS Institutions of Higher Learning","3825 Ridgewood Road  Suite 334",NULL,NULL,NULL,"2010",NULL,"o","g","ZZ","ot","N",NULL,"10EDHMS002020100929","MS"
"dce6cc6b47be826b03f5729738ed97a2","active","201006291","17.310",NULL,"MULTIPLE RECIPIENTS",NULL,NULL,"025",NULL,"21",NULL,"1635",NULL,NULL,"175000",NULL,"175000","2010-03-31","2010-01-01","2010-03-31","10","1",NULL,NULL,"04**025","ARIZONA","YAVAPAI",NULL,"03  ","Energy Employees Occupational Illness Compensation","Employment Standards Administration  Department of Labor","ENERGY EMPLOYEES OCCUPATIONAL ILLNESS COMPENSATION.",NULL,NULL,"16","1523","000",NULL,NULL,NULL,NULL,NULL,"2010","AZ","i","d","ZZ","16","N","USA","17.310-ARIZONA-YAVAPAI-20100331-10","AZ"
"15de92034664663f55b0044b97d0deae","active","201006291","17.310",NULL,"MULTIPLE RECIPIENTS",NULL,NULL,"059",NULL,"21",NULL,"1635",NULL,NULL,"75000",NULL,"75000","2010-03-31","2010-01-01","2010-03-31","10","1",NULL,NULL,"51**059","VIRGINIA","FAIRFAX",NULL,"90  ","Energy Employees Occupational Illness Compensation","Employment Standards Administration  Department of Labor","ENERGY EMPLOYEES OCCUPATIONAL ILLNESS COMPENSATION.",NULL,NULL,"16","1523","000",NULL,NULL,NULL,NULL,NULL,"2010","VA","i","d","ZZ","16","N","USA","17.310-VIRGINIA-FAIRFAX-20100331-10","VA"
"25d61e047db8db4423a192e529bd39db","active","201010051","64.114",NULL,"MULTIPLE RECIPIENTS",NULL,NULL,"149",NULL,"21","(none)","3640",NULL,NULL,NULL,NULL,NULL,"2010-09-28",NULL,NULL,"08","1",NULL,NULL,"18149**","INDIANA","STARKE",NULL,"    ",NULL,"VA- VETERANS BENEFIT ADMINISTRATION",NULL,NULL,"  ","  ",NULL,"   ",NULL,NULL,NULL,"30040","-128","2010","IN","i","l","ZZ","36","N",NULL,"64114201009727","IN"
"239422b6dd7b2a88d8ff5e0bab119532","active","201010051","64.114",NULL,"MULTIPLE RECIPIENTS",NULL,NULL,"019",NULL,"21","(none)","3640",NULL,NULL,NULL,NULL,NULL,"2010-09-28",NULL,NULL,"08","1",NULL,NULL,"41019**","OREGON","DOUGLAS",NULL,"    ",NULL,"VA- VETERANS BENEFIT ADMINISTRATION",NULL,NULL,"  ","  ",NULL,"   ",NULL,NULL,NULL,"534491","-3310","2010","OR","i","l","ZZ","36","N",NULL,"6411420100982","OR"
"d80da494988d362aa74ed68b7e35eda1","active","201005141","31.007","SAI EXEMPT","LUDLUM MEASUREMENTS INC","71540","SWEETWATER","353","795563209","23","B","8300","09425204ST0003",NULL,"600000",NULL,"600000","2010-02-24","2010-03-01","2011-03-01","09","2","C",NULL,"4871540","TX","SWEETWATER","795563209","TX11","EXPORT - LOAN GUARANTEE/INSURED LOANS","EXPORT-IMPORT BANK OF THE UNITED STATES","EXPORT INSURANCE","008025447","10","83","4162","   ","501 OAK ST",NULL,NULL,NULL,NULL,"2010","TX","f","i","TX11","ot","N","USA",NULL,"TX"
"f9e7a41d8585b0e0cb2b52a9f4bd26f4","active","201004053","10.450",NULL,"ACE PROPERTY AND CASUALTY","60000","Philadelphia","101","191063703","22","A","12D4","A&O2010RH022010",NULL,"10485897",NULL,NULL,"2010-02-24","2010-01-25","2010-02-24","09","2",NULL,NULL,"1939765","IOWA","Johnston","501313006","IA03",NULL,"Risk Management Agency (08)","Standard Reinsurance Agreement for ACE PROPERTY AND CASUALTY  for RY 2010 for 022010","090362109","08","12","4085",NULL,"436 Walnut Street",NULL,NULL,NULL,NULL,"2010","IA","f","i","ZZ","12","N","USA","12D400A&O2010RH022010       12X4085","TX"
"01db4707cf4c5d6d021697f3f31f6b9f","active","201010051","10.998","SAI EXEMPT","MISSOURI SYSTEM UNIVERSITY","15670","COLUMBIA","019","652111230","06","A","12D3","9069910","1","38519",NULL,NULL,"2010-02-01","2009-10-01","2010-09-30","11","2",NULL,NULL,"29019","MISSOURI","COLUMBIA","652113020","MO09",NULL,"Foreign Agricultural Service (10)","FAS LONG TERM STANDING AGREEMENTS FOR STORAGE  TRANSPORTATION AND LEASE","153890272","11","12","2900","   ","310 JESSE HALL",NULL,NULL,NULL,NULL,"2010","MO","h","o","MO09","12","N","USA","12D3019069910         1     1282900","MO"
"e492d89d31b84482175215714d54ed3d","active","201010051","10.998","SAI EXEMPT","EUMOTIF  INC.","65000","SCOTTSDALE","013","852602490","22","A","12D3","9069806","1","754",NULL,NULL,"2010-03-01","2009-10-01","2010-09-30","11","2",NULL,NULL,"04013","ARIZONA","SCOTTSDALE","852602441","AZ05",NULL,"Foreign Agricultural Service (10)","FAS LONG TERM STANDING AGREEMENTS FOR STORAGE  TRANSPORTATION AND LEASE","116899969","11","12","2900","   ","14605 NORTH AIRPORT DRIVE",NULL,NULL,NULL,NULL,"2010","AZ","f","o","AZ05","12","N","USA","12D3019069806         1     1282900","AZ"
        ''', grants_file.name)

    def test_prepare_contracts_file(self):
        grants_file = NamedTemporaryFile('w')
        contracts_file = NamedTemporaryFile('w')

        out_dir = os.path.dirname(grants_file.name)

        USASpendingDenormalizer().parse_directory(os.path.join(os.path.dirname(__file__), 'test_data/usaspending'), out_dir, grants_file.name, contracts_file.name)

        self.assert_file_contents_eq('''
"37adc9010a603b98304be859dad2695e","active","GOVPLACE",NULL,"7014","Automation Modernization, Customs and Border Protection","HSBP1010J00525","0",NULL,"0","7001","HSHQDC07D00025","N","0","2010-08-12","2010-07-30","2010-08-29","2010-08-29","616022.120000","f","616022.120000","f","f","616022.120000","7014","f","ITCD","f","7014","f","f","ITCD",NULL,"f","X","f","f","C","J","f",NULL,"f",NULL,"N: No",NULL,NULL,"f","Brocade switches","f","f","f","f","X","f","X","X","f",NULL,"f","1",NULL,NULL,NULL,"t","X","7050","D",NULL,"541519","C","f",NULL,"f",NULL,"E","US","D","15707 ROCKFIELD BLVD STE 305",NULL,NULL,"IRVINE","CA","926182829","USA","9570508830000","48",NULL,"VA","US","221503224",NULL,"11","D",NULL,"MAFO","SBA",NULL,"NONE","30",NULL,"20000000.000000","FAIR",NULL,"5","A",NULL,"f","f","f","f","f","f",NULL,NULL,"S",NULL,"957050883","2010","GOVPLACE","70","70","CA48","VA11","70","0531",NULL,NULL,"c"
"0d42d94514b1a7031be23d1974c5e1bb","active","SUPREME FOODSERVICE AG",NULL,"9700",NULL,"610G","0",NULL,"0","9700","SPM30008D3153","N","0","2010-07-03","2010-07-03","2010-07-12","2010-07-12","77431.000000","f","77431.000000","f","f","77431.000000","97AS","f","SPM300","f","97AS","f","f","SPM300",NULL,"f","X","f","f","C","J","f",NULL,"f",NULL,"N: No",NULL,"X","f","4514806667OTHER GROCERY AND RE","f","f","t","f","X","f","X",NULL,"f","Z","f","1",NULL,NULL,NULL,"f","X","8910","D","B2","424490","C","f","000","f","Z","E","SZ","E","ZIEGELBRUECKSTRASSE 66",NULL,NULL,"ZIEGELBRUECKE",NULL,"8866","CHE","4813475520000",NULL,NULL,NULL,"SZ",NULL,NULL,NULL,"A",NULL,"NP","NONE","INTERNATIONAL ORG","NONE","2073",NULL,"700000000.000000",NULL,NULL,"5","A",NULL,"f","f","f","f","f","f",NULL,NULL,"O",NULL,"400210806","2010","SUPREME GROUP HOLDING SARL","97","89","ZZ","ZZ",NULL,NULL,NULL,NULL,"c"
        ''', contracts_file.name)


    def assert_file_contents_eq(self, expected_contents, actual_file_path):
        self.maxDiff = None
        self.assertEqual(self.ignore_empty_lines(expected_contents), self.ignore_empty_lines(open(actual_file_path, "r").read()))

    def ignore_empty_lines(self, values):
        if type(values) != type([]):
            values = values.split("\n")

        return [ x for x in values if re.search(r'[^ ]', x) ]


class TestLoader(TestCase):

    def test_loader_faads_sql(self):
        sql = """
COPY grants_grant
(unique_transaction_id, transaction_status, fyq, cfda_program_num, sai_number, recipient_name, recipient_city_code, recipient_city_name, recipient_county_code, recipient_zip, recipient_type, action_type, agency_code, federal_award_id, federal_award_mod, fed_funding_amount, non_fed_funding_amount, total_funding_amount, obligation_action_date, starting_date, ending_date, assistance_type, record_type, correction_late_ind, fyq_correction, principal_place_code, principal_place_state, principal_place_cc, principal_place_zip, principal_place_cd, cfda_program_title, agency_name, project_description, duns_no, duns_conf_code, progsrc_agen_code, progsrc_acnt_code, progsrc_subacnt_code, receip_addr1, receip_addr2, receip_addr3, face_loan_guran, orig_sub_guran, fiscal_year, principal_place_state_code, recip_cat_type, asst_cat_type, recipient_cd, maj_agency_cat, rec_flag, recipient_country_code, uri, recipient_state_code)
FROM '/home/kwebb/GIANT/usapsending/20101101_csv/datafeeds/out/grants.out'
CSV QUOTE '"'
        """

        self.assert_eq_ignoring_leading_trailing_space(sql, Loader().make_faads_sql('/home/kwebb/GIANT/usapsending/20101101_csv/datafeeds/out/grants.out'))


    def test_loader_fpds_sql(self):
        sql = """
COPY contracts_contract
(unique_transaction_id, transaction_status, vendorname, lastdatetoorder, agencyid, account_title, piid, modnumber, vendordoingasbusinessname, transactionnumber, idvagencyid, idvpiid, aiobflag, idvmodificationnumber, signeddate, effectivedate, currentcompletiondate, ultimatecompletiondate, obligatedamount, shelteredworkshopflag, baseandexercisedoptionsvalue, veteranownedflag, srdvobflag, baseandalloptionsvalue, contractingofficeagencyid, womenownedflag, contractingofficeid, minorityownedbusinessflag, fundingrequestingagencyid, saaobflag, apaobflag, fundingrequestingofficeid, purchasereason, baobflag, fundedbyforeignentity, haobflag, naobflag, contractactiontype, typeofcontractpricing, verysmallbusinessflag, reasonformodification, federalgovernmentflag, majorprogramcode, costorpricingdata, solicitationid, costaccountingstandardsclause, stategovernmentflag, descriptionofcontractrequirement, localgovernmentflag, gfe_gfp, seatransportation, consolidatedcontract, lettercontract, multiyearcontract, performancebasedservicecontract, contingencyhumanitarianpeacekeepingoperation, tribalgovernmentflag, contractfinancing, purchasecardaspaymentmethod, numberofactions, walshhealyact, servicecontractact, davisbaconact, clingercohenact, interagencycontractingauthority, productorservicecode, contractbundling, claimantprogramcode, principalnaicscode, recoveredmaterialclauses, educationalinstitutionflag, systemequipmentcode, hospitalflag, informationtechnologycommercialitemcategory, useofepadesignatedproducts, countryoforigin, placeofmanufacture, streetaddress, streetaddress2, streetaddress3, city, state, zipcode, vendorcountrycode, dunsnumber, congressionaldistrict, locationcode, statecode, placeofperformancecountrycode, placeofperformancezipcode, nonprofitorganizationflag, placeofperformancecongressionaldistrict, extentcompeted, competitiveprocedures, solicitationprocedures, typeofsetaside, organizationaltype, evaluatedpreference, numberofemployees, research, annualrevenue, statutoryexceptiontofairopportunity, reasonnotcompeted, numberofoffersreceived, commercialitemacquisitionprocedures, hbcuflag, commercialitemtestprogram, smallbusinesscompetitivenessdemonstrationprogram, a76action, sdbflag, firm8aflag, hubzoneflag, phoneno, faxno, contractingofficerbusinesssizedetermination, otherstatutoryauthority, eeparentduns, fiscal_year, mod_parent, maj_agency_cat, psc_cat, vendor_cd, pop_cd, progsourceagency, progsourceaccount, progsourcesubacct, rec_flag, type_of_contract)
FROM '/home/kwebb/GIANT/usapsending/20101101_csv/datafeeds/out/contracts.out'
CSV QUOTE '"'
        """

        self.assert_eq_ignoring_leading_trailing_space(sql, Loader().make_fpds_sql('/home/kwebb/GIANT/usapsending/20101101_csv/datafeeds/out/contracts.out'))


    def test_insert_faads(self):
        Loader().insert_faads(os.path.join(os.path.dirname(__file__), 'test_data/usaspending/out/grants.out'))

        cursor = connections['default'].cursor()
        cursor.execute('select count(*) from grants_grant')
        count = cursor.fetchone()[0]

        self.assertEqual(10, count)


    def assert_eq_ignoring_leading_trailing_space(self, expected, actual):
        self.maxDiff = None
        self.assertEqual(self.strip_lines(expected), self.strip_lines(actual))


    def strip_lines(self, values):
        if type(values) != type([]):
            values = values.split("\n")

        return [ x.strip() for x in values if re.search(r'[^ ]', x) ]



