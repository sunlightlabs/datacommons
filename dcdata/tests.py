from cStringIO import StringIO
from dcdata import processor
from dcdata.contracts.models import Contract
from dcdata.contribution.models import Contribution
from dcdata.contribution.sources.crp import FILE_TYPES
from dcdata.earmarks.models import Earmark, Member
from dcdata.loading import model_fields, LoaderEmitter
from dcdata.management.commands.crp_denormalize import load_candidates, \
    load_committees
from dcdata.management.commands.crp_denormalize_individuals import \
    CRPDenormalizeIndividual
from dcdata.management.commands.loadcontributions import LoadContributions, \
    ContributionLoader, StringLengthFilter
from dcdata.management.commands.loadearmarks import FIELDS as EARMARK_FIELDS, \
    LoadTCSEarmarks, save_earmark, _normalize_locations, split_and_transpose
from dcdata.management.commands.nimsp_denormalize import NIMSPDenormalize
from dcdata.models import Import
from dcdata.processor import load_data, chain_filters, compose_one2many, \
    SkipRecordException
from dcdata.scripts.usaspending.converter import USASpendingDenormalizer
from dcdata.scripts.usaspending.contracts_loader import Loader as ContractsLoader
from dcdata.scripts.usaspending.grants_loader import Loader as GrantsLoader
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
from settings import LOADING_DIRECTORY
from scripts.nimsp.common import CSV_SQL_MAPPING
from scripts.nimsp.salt import DCIDFilter, SaltFilter
from updates import edits, update
import os
import os.path
import re
import shutil
import sqlite3
import sys



dataroot = os.path.join(LOADING_DIRECTORY, 'test_data')

def assert_record_contains(tester, expected, actual):
    for (name, value) in expected.iteritems():
        tester.assertEqual(value, actual[name])



class TestRecipientFilter(TestCase):

    @attr('crp')
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

    def setUp(self):
        shutil.copy(self.original_salts_db_path, self.salts_db_path)

    def tearDown(self):
        output_paths = [
            os.path.join(NIMSPDenormalize.OUT_DIR, 'nimsp_allocated_contributions.csv'),
            os.path.join(NIMSPDenormalize.OUT_DIR, 'nimsp_unallocated_contributions.csv'),
            self.salts_db_path
        ]

        for path in output_paths:
            if os.path.exists(path):
                os.remove(path)


    @attr('nimsp')
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


    @attr('nimsp')
    def test_command_do_for_file(self):
        nd = NIMSPDenormalize()
        nd.do_for_file(os.path.join(dataroot, 'denormalized/nimsp_partial_denormalization.csv'))

        allocated_path = os.path.join(NIMSPDenormalize.OUT_DIR, 'nimsp_allocated_contributions.csv')
        unallocated_path = os.path.join(NIMSPDenormalize.OUT_DIR, 'nimsp_unallocated_contributions.csv')
        self.assertEqual(9, sum(1 for _ in open(allocated_path, 'r')))
        self.assertEqual(4, sum(1 for _ in open(unallocated_path, 'r')))

        os.remove(allocated_path)
        os.remove(unallocated_path)


    def test_recipient_state(self):
        """
            The call to test_command, below, originally accessed the 'loadcontributions' command,
            which has been removed because it was testing too much at once. This test, since it
            tests only loaded contributions, should be rewritten and moved elsewhere. (TODO)
        """
        raise SkipTest
        self.test_command()

        self.assertEqual(7, Contribution.objects.filter(recipient_state='OR').count())
        self.assertEqual(2, Contribution.objects.filter(recipient_state='WA').count())


    @attr('nimsp')
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


    @attr('nimsp')
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

    @attr('crp')
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

    @attr('crp')
    def test_command(self):

        if os.path.exists(self.output_path):
            os.remove(self.output_path)

        call_command('crp_denormalize_individuals', cycles='08', dataroot=dataroot)

        input_path = os.path.join(dataroot, 'raw/crp/indivs08.txt')
        self.assertEqual(10, sum(1 for _ in open(input_path, 'r')))
        self.assertEqual(11, sum(1 for _ in open(self.output_path, 'r')))

    @attr('crp')
    def test_process_record(self):

        input_values = ["2000","0011161","f0000263005 ","VAN SYCKLE, LORRAINE E","C00040998","","","T2300","02/22/1999","200","","BANGOR","ME","04401","PB","15 ","C00040998","","F","VAN SYCKLE LM","99034391444","","","P/PAC"]
        self.assert_row_succeeds(input_values)

    @attr('crp')
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


    @attr('crp')
    def assert_row_succeeds(self, input_values):
        self.assertEqual(len(FILE_TYPES['indivs']), len(input_values))
        input_record = dict(zip(FILE_TYPES['indivs'], input_values))

        record_processor = CRPDenormalizeIndividual.get_record_processor({}, {}, {})
        output_records = record_processor(input_record)

        self.assertEqual(1, len(output_records))
        self.assertEqual(set(model_fields('contribution.Contribution')), set(output_records[0].keys()))

class TestCRPDenormalizePac2Candidate(TestCase):
    output_path = os.path.join(dataroot, 'denormalized/denorm_pac2cand.txt')

    @attr('crp')
    def test_command(self):

        if os.path.exists(self.output_path):
            os.remove(self.output_path)

        call_command('crp_denormalize_pac2candidate', cycles='08', dataroot=dataroot)

        input_path = os.path.join(dataroot, 'raw/crp/pacs08.txt')
        self.assertEqual(10, sum(1 for _ in open(input_path, 'r')))
        self.assertEqual(11, sum(1 for _ in open(self.output_path, 'r')))


class TestCRPDenormalizePac2Pac(TestCase):
    output_path = os.path.join(dataroot, 'denormalized/denorm_pac2pac.txt')

    @attr('crp')
    def test_command(self):

        if os.path.exists(self.output_path):
            os.remove(self.output_path)

        call_command('crp_denormalize_pac2pac', cycles='08', dataroot=dataroot)

        input_path = os.path.join(dataroot, 'raw/crp/pac_other08.txt')
        self.assertEqual(10, sum(1 for _ in open(input_path, 'r')))
        self.assertEqual(11, sum(1 for _ in open(self.output_path, 'r')))


class TestLoadContributions(TestCase):


    @attr('crp')
    def test_command(self):
        call_command('crp_denormalize_individuals', cycles='08', dataroot=dataroot)
        call_command('loadcontributions', os.path.join(dataroot, 'denormalized/denorm_indivs.08.txt'))

        self.assertEqual(10, Contribution.objects.all().count())

    @attr('crp')
    def test_skip(self):
        call_command('crp_denormalize_individuals', cycles='08', dataroot=dataroot)
        call_command('loadcontributions', os.path.join(dataroot, 'denormalized/denorm_indivs.08.txt'), skip='3')

        self.assertEqual(7, Contribution.objects.all().count())

    @attr('crp')
    def test_decimal_amounts(self):
        """ See ticket #177. """

        input_row = ["2000","0011161","f0000263005 ","VAN SYCKLE, LORRAINE E","C00040998","","","T2300","02/22/1999","123.45","","BANGOR","ME","04401","PB","15 ","C00040998","","F","VAN SYCKLE LM","99034391444","","","P/PAC"]
        input_record = dict(zip(FILE_TYPES['indivs'], input_row))
        denormalized_records = list()
        denormalizer = CRPDenormalizeIndividual.get_record_processor({}, {}, {})

        load_data([input_record], denormalizer, denormalized_records.append)

        print denormalized_records[0]

        self.assertEqual(1, len(denormalized_records))
        self.assertEqual(u'123.45', denormalized_records[0]['amount'])

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

    @attr('crp')
    @attr('nimsp')
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
        
        
    @attr('crp')
    @attr('nimsp')
    @attr('crp_bogus_warnings')
    def test_bogus_warnings(self):
        """ When running the full loadcontributions, I get about 1.7M warnings of records with extra fields.
        Something very mysterious is going on b/c the data is still laoded correctly, despite the warnings
        showing misformed data. Plus, just being in the exception shandler should've meant that the records
        aren't loaded, but they are. Here in the unit test there's no problem. So I have no idea where these
        warnings are coming from. See note in ticket #735.
        """
        input_rows = [',,2010,urn:fec:transaction,pac2pac:2010:1477454,24k,10990744132,False,5000.0,2010-05-10,National Auto Dealers Assn,C00040998,committee,,,,,WASHINGTON,DC,20003,T2300,National Auto Dealers Assn,,,,Every Republican is Crucial PAC,C00384701,R,committee,,,J2200,Every Republican is Crucial PAC,C00384701,R,,,,,,,']

        loader = ContributionLoader(
            source='unittest',
            description='unittest',
            imported_by='unittest'
        )
        source = VerifiedCSVSource(input_rows, model_fields('contribution.Contribution'))
        processor = LoadContributions.get_record_processor(loader.import_session)
        output = LoaderEmitter(loader).process_record

        load_data(source, processor, output)

        self.assertEqual(1, Contribution.objects.all().count())


class TestProcessor(TestCase):

    @attr('nimsp')
    @attr('crp')
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

    @attr('nimsp')
    @attr('crp')
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

    @attr('nimsp')
    @attr('crp')
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

    @attr('nimsp')
    @attr('crp')
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

    @attr('nimsp')
    @attr('crp')
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

    @attr('usaspending')
    @attr('grants')
    def test_prepare_grants_file(self):
        in_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_data/usaspending')
        out_dir = os.path.join(in_dir, 'out')

        USASpendingDenormalizer().parse_directory(in_dir, out_dir)

        self.assert_file_contents_eq('''
dce6cc6b47be826b03f5729738ed97a2|active|201006291|17.310||MULTIPLE RECIPIENTS|||YAVAPAI|025||USA|21||1635|||175000|0|175000|2010-03-31|2010-01-01|2010-03-31|10|1|||04**025|ARIZONA|YAVAPAI||03  |Energy Employees Occupational Illness Compensation|Employment Standards Administration  Department of Labor|ENERGY EMPLOYEES OCCUPATIONAL ILLNESS COMPENSATION.|||16|1523|000||||0|0|2010|AZ|i|d|ZZ|16|N|17.310-ARIZONA-YAVAPAI-20100331-10|AZ|20110111
15de92034664663f55b0044b97d0deae|active|201006291|17.310||MULTIPLE RECIPIENTS|||FAIRFAX|059||USA|21||1635|||75000|0|75000|2010-03-31|2010-01-01|2010-03-31|10|1|||51**059|VIRGINIA|FAIRFAX||90  |Energy Employees Occupational Illness Compensation|Employment Standards Administration  Department of Labor|ENERGY EMPLOYEES OCCUPATIONAL ILLNESS COMPENSATION.|||16|1523|000||||0|0|2010|VA|i|d|ZZ|16|N|17.310-VIRGINIA-FAIRFAX-20100331-10|VA|20110111
c9b7090891d057c1336d6ae5f902243d|active|201010041|94.016|SAI NOT AVAILABLE|Hope for the Aged Inc.|06593|Bayaman|Bayamon|021|00956||12|A|9577|10SCAPR001|0|282687|49576|332263|2010-09-07|2010-09-30|2013-09-29|04|2|||7206593|Puerto Rico|Bayamon|00956|98  |Senior Companion Program|Corporation for National and Community Service|Senior Companion Program|146240820|8 |95|2728|000|Calle Duende 2 G1|Lomas Verdes||0|0|2010|PR|n|g|ZZ|ot|N|10SCAPR001020100907|PR|20110111
8a9788a5623095aabcb2d34fe57a4f67|active|201010041|94.006|SAI NOT AVAILABLE|Mississippi Institutions of Higher Learning|36000|Jackson|Hinds|049|392116453||25|A|9577|10EDHMS002|0|160000|0|160000|2010-09-29|2010-09-29|2011-07-31|04|2|||00*****|Mississippi|Hinds|392116453|00  |AmeriCorps|Corporation for National and Community Service|Education Awards Program|023659365|8 |95|2728|000|MS Institutions of Higher Learning|3825 Ridgewood Road  Suite 334||0|0|2010||o|g|ZZ|ot|N|10EDHMS002020100929|MS|20110111
d80da494988d362aa74ed68b7e35eda1|active|201005141|31.007|SAI EXEMPT|LUDLUM MEASUREMENTS INC|71540|SWEETWATER|NOLAN|353|795563209|USA|23|B|8300|09425204ST0003||600000|0|600000|2010-02-24|2010-03-01|2011-03-01|09|2|C||4871540|TX|SWEETWATER|795563209|TX11|EXPORT - LOAN GUARANTEE/INSURED LOANS|EXPORT-IMPORT BANK OF THE UNITED STATES|EXPORT INSURANCE|008025447|10|83|4162|   |501 OAK ST|||0|0|2010|TX|f|i|TX11|ot|N||TX|20110111
f9e7a41d8585b0e0cb2b52a9f4bd26f4|active|201004053|10.450||ACE PROPERTY AND CASUALTY|60000|Philadelphia|Philadelphia|101|191063703|USA|22|A|12D4|A&O2010RH022010||10485897|0|0|2010-02-24|2010-01-25|2010-02-24|09|2|||1939765|IOWA|Johnston|501313006|IA03||Risk Management Agency (08)|Standard Reinsurance Agreement for ACE PROPERTY AND CASUALTY  for RY 2010 for 022010|090362109|08|12|4085||436 Walnut Street|||0|0|2010|IA|f|i|ZZ|12|N|12D400A&O2010RH022010       12X4085|TX|20110111
25d61e047db8db4423a192e529bd39db|active|201010051|64.114||MULTIPLE RECIPIENTS|||STARKE|149|||21|(none)|3640|||0|0|0|2010-09-28|||08|1|||18149**|INDIANA|STARKE||    ||VA- VETERANS BENEFIT ADMINISTRATION|||  |  ||   ||||30040|-128|2010|IN|i|l|ZZ|36|N|64114201009727|IN|20110111
239422b6dd7b2a88d8ff5e0bab119532|active|201010051|64.114||MULTIPLE RECIPIENTS|||DOUGLAS|019|||21|(none)|3640|||0|0|0|2010-09-28|||08|1|||41019**|OREGON|DOUGLAS||    ||VA- VETERANS BENEFIT ADMINISTRATION|||  |  ||   ||||534491|-3310|2010|OR|i|l|ZZ|36|N|6411420100982|OR|20110111
01db4707cf4c5d6d021697f3f31f6b9f|active|201010051|10.998|SAI EXEMPT|MISSOURI SYSTEM UNIVERSITY|15670|COLUMBIA|Boone|019|652111230|USA|06|A|12D3|9069910|1|38519|0|0|2010-02-01|2009-10-01|2010-09-30|11|2|||29019|MISSOURI|COLUMBIA|652113020|MO09||Foreign Agricultural Service (10)|FAS LONG TERM STANDING AGREEMENTS FOR STORAGE  TRANSPORTATION AND LEASE|153890272|11|12|2900|   |310 JESSE HALL|||0|0|2010|MO|h|o|MO09|12|N|12D3019069910         1     1282900|MO|20110111
e492d89d31b84482175215714d54ed3d|active|201010051|10.998|SAI EXEMPT|EUMOTIF  INC.|65000|SCOTTSDALE|Maricopa|013|852602490|USA|22|A|12D3|9069806|1|754|0|0|2010-03-01|2009-10-01|2010-09-30|11|2|||04013|ARIZONA|SCOTTSDALE|852602441|AZ05||Foreign Agricultural Service (10)|FAS LONG TERM STANDING AGREEMENTS FOR STORAGE  TRANSPORTATION AND LEASE|116899969|11|12|2900|   |14605 NORTH AIRPORT DRIVE|||0|0|2010|AZ|f|o|AZ05|12|N|12D3019069806         1     1282900|AZ|20110111
       ''', os.path.join(out_dir, 'grants.out'))

    @attr('usaspending')
    @attr('contracts')
    def test_prepare_contracts_file(self):
        in_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_data/usaspending')
        out_dir = os.path.join(in_dir, 'out')

        USASpendingDenormalizer().parse_directory(in_dir, out_dir)

        self.assert_file_contents_eq('''
37adc9010a603b98304be859dad2695e|active|GOVPLACE||7014|Automation Modernization, Customs and Border Protection|HSBP1010J00525|0||0|7001|HSHQDC07D00025|N|0|2010-08-12|2010-07-30|2010-08-29|2010-08-29|616022.12|f|616022.12|f|f|616022.12|7014|f|ITCD|f|7014|f|f|ITCD||f|X|f|f|C|J|f||f||N: No|||f|Brocade switches|f|f|f|f|X|f|X|X|f||f|1||||t|X|7050|D||541519|C|f||f||E|US|D|15707 ROCKFIELD BLVD STE 305|||IRVINE|CA|926182829|USA|9570508830000|48||VA|US|221503224||11|D||MAFO|SBA||NONE|30||20000000.0|FAIR||5|A||f|f|f|f|f|f|||S||957050883|2010|GOVPLACE|70|70|CA48|VA11|70|0531|||c|||
0d42d94514b1a7031be23d1974c5e1bb|active|SUPREME FOODSERVICE AG||9700||610G|0||0|9700|SPM30008D3153|N|0|2010-07-03|2010-07-03|2010-07-12|2010-07-12|77431.0|f|77431.0|f|f|77431.0|97AS|f|SPM300|f|97AS|f|f|SPM300||f|X|f|f|C|J|f||f||N: No||X|f|4514806667OTHER GROCERY AND RE|f|f|t|f|X|f|X||f|Z|f|1||||f|X|8910|D|B2|424490|C|f|000|f|Z|E|SZ|E|ZIEGELBRUECKSTRASSE 66|||ZIEGELBRUECKE||8866|CHE|4813475520000||||SZ||||A||NP|NONE|INTERNATIONAL ORG|NONE|2073||700000000.0|||5|A||f|f|f|f|f|f|||O||400210806|2010|SUPREME GROUP HOLDING SARL|97|89|ZZ|ZZ|||||c|||
        ''', os.path.join(out_dir, 'contracts.out'))

    def assert_file_contents_eq(self, expected_contents, actual_file_path):
        self.maxDiff = None
        self.assertEqual(self.ignore_empty_lines(expected_contents), self.ignore_empty_lines(open(actual_file_path, "r").read()))

    def ignore_empty_lines(self, values):
        if type(values) != type([]):
            values = values.split("\n")

        return [ x for x in values if re.search(r'[^ ]', x) ]


class TestContractsLoader(TestCase):

    @attr('usaspending')
    @attr('contracts')
    @attr('usaspending_split_unicode')
    def test_split_unicode(self):
        contracts_file = 'test_data/usaspending/out/contracts.out'

        out_dir = os.path.dirname(contracts_file)

        USASpendingDenormalizer().parse_directory(os.path.join(os.path.dirname(__file__), 'test_data/usaspending/bad_unicode'), out_dir)

        ContractsLoader().insert_fpds(os.path.join(os.path.dirname(__file__), 'test_data/usaspending/out/contracts.out'))

        self.assertEqual(1, Contract.objects.all().count())

        expected_program_code = 'FREQUENCY UP-CONVERSION DETECTION SYSTEM WITH SINGLE PHOTON SENSITIVITY WITHIN 1-1.8 \xc3\x82\xc2\xb5M AND 3-4 \xc3\x82\xc2\xb5M'

        self.assertEqual(expected_program_code.decode('utf8'), Contract.objects.all()[0].majorprogramcode)


    def setUp(self):
        contracts_file = 'test_data/usaspending/out/contracts.out'

        out_dir = os.path.dirname(os.path.abspath(contracts_file))

        USASpendingDenormalizer().parse_directory(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_data/usaspending'), out_dir)


    @attr('usaspending')
    @attr('grants')
    def test_loader_faads_sql(self):

        sql = """
COPY grants_grant
(unique_transaction_id, transaction_status, fyq, cfda_program_num, sai_number, recipient_name, recipient_city_code, recipient_city_name, recipient_county_name, recipient_county_code, recipient_zip, recipient_country_code, recipient_type, action_type, agency_code, federal_award_id, federal_award_mod, fed_funding_amount, non_fed_funding_amount, total_funding_amount, obligation_action_date, starting_date, ending_date, assistance_type, record_type, correction_late_ind, fyq_correction, principal_place_code, principal_place_state, principal_place_cc, principal_place_zip, principal_place_cd, cfda_program_title, agency_name, project_description, duns_no, duns_conf_code, progsrc_agen_code, progsrc_acnt_code, progsrc_subacnt_code, receip_addr1, receip_addr2, receip_addr3, face_loan_guran, orig_sub_guran, fiscal_year, principal_place_state_code, recip_cat_type, asst_cat_type, recipient_cd, maj_agency_cat, rec_flag, uri, recipient_state_code, imported_on)
FROM 'test_data/usaspending/out/grants.out'
CSV QUOTE '"'
        """

        self.assert_eq_ignoring_leading_trailing_space(sql, GrantsLoader().sql_str(os.path.abspath('./test_data/usaspending/out/grants.out')))


    @attr('usaspending')
    @attr('contracts')
    def test_loader_fpds_sql(self):
        sql = """
COPY contracts_contract
(unique_transaction_id, transaction_status, vendorname, lastdatetoorder, agencyid, account_title, piid, modnumber, vendordoingasbusinessname, transactionnumber, idvagencyid, idvpiid, aiobflag, idvmodificationnumber, signeddate, effectivedate, currentcompletiondate, ultimatecompletiondate, obligatedamount, shelteredworkshopflag, baseandexercisedoptionsvalue, veteranownedflag, srdvobflag, baseandalloptionsvalue, contractingofficeagencyid, womenownedflag, contractingofficeid, minorityownedbusinessflag, fundingrequestingagencyid, saaobflag, apaobflag, fundingrequestingofficeid, purchasereason, baobflag, fundedbyforeignentity, haobflag, naobflag, contractactiontype, typeofcontractpricing, verysmallbusinessflag, reasonformodification, federalgovernmentflag, majorprogramcode, costorpricingdata, solicitationid, costaccountingstandardsclause, stategovernmentflag, descriptionofcontractrequirement, localgovernmentflag, gfe_gfp, seatransportation, consolidatedcontract, lettercontract, multiyearcontract, performancebasedservicecontract, contingencyhumanitarianpeacekeepingoperation, tribalgovernmentflag, contractfinancing, purchasecardaspaymentmethod, numberofactions, walshhealyact, servicecontractact, davisbaconact, clingercohenact, interagencycontractingauthority, productorservicecode, contractbundling, claimantprogramcode, principalnaicscode, recoveredmaterialclauses, educationalinstitutionflag, systemequipmentcode, hospitalflag, informationtechnologycommercialitemcategory, useofepadesignatedproducts, countryoforigin, placeofmanufacture, streetaddress, streetaddress2, streetaddress3, city, state, zipcode, vendorcountrycode, dunsnumber, congressionaldistrict, locationcode, statecode, placeofperformancecountrycode, placeofperformancezipcode, nonprofitorganizationflag, placeofperformancecongressionaldistrict, extentcompeted, competitiveprocedures, solicitationprocedures, typeofsetaside, organizationaltype, evaluatedpreference, numberofemployees, research, annualrevenue, statutoryexceptiontofairopportunity, reasonnotcompeted, numberofoffersreceived, commercialitemacquisitionprocedures, hbcuflag, commercialitemtestprogram, smallbusinesscompetitivenessdemonstrationprogram, a76action, sdbflag, firm8aflag, hubzoneflag, phoneno, faxno, contractingofficerbusinesssizedetermination, otherstatutoryauthority, eeparentduns, fiscal_year, mod_parent, maj_agency_cat, psc_cat, vendor_cd, pop_cd, progsourceagency, progsourceaccount, progsourcesubacct, rec_flag, type_of_contract, agency_name, contracting_agency_name, requesting_agency_name)
FROM '/home/akr/work/datacommons/test_data/usaspending/out/contracts.out'
CSV QUOTE \'"\'
        """

        self.assert_eq_ignoring_leading_trailing_space(sql, ContractsLoader().sql_str(os.path.abspath('./test_data/usaspending/out/contracts.out')))


    @attr('usaspending')
    @attr('grants')
    def test_insert_faads(self):
        GrantsLoader().insert_faads(os.path.join(os.path.dirname(__file__), 'test_data/usaspending/out/grants.out'))

        cursor = connections['default'].cursor()
        cursor.execute('select count(*) from grants_grant')
        count = cursor.fetchone()[0]

        self.assertEqual(10, count)

    @attr('usaspending')
    @attr('contracts')
    def test_insert_fpds(self):
        ContractsLoader().insert_fpds(os.path.join(os.path.dirname(__file__), 'test_data/usaspending/out/contracts.out'))

        cursor = connections['default'].cursor()
        cursor.execute('select count(*) from contracts_contract')
        count = cursor.fetchone()[0]

        self.assertEqual(2, count)

    @attr('usaspending')
    @attr('contracts')
    def test_fpds_quoting(self):
        # this test will fail with a DB error. I believe the code is correct--works when run from psql.
        # appears that psycopg's copy_from doesn't correctly interpret quoted fields.
        raise SkipTest

        input = StringIO('1b649a7c08ba717c09abd378c660dba1|active|DELL MARKETING LIMITED PARTNERSHIP||4735||GST0904DF3801|AO02||0|4730|GS35F4076D|N|0|2004-11-09|2004-11-09|2004-11-09|2004-11-09|-0.02|f|-0.02|f|f|-0.02|4735|f|DF000|f|1700|f|f|N62271||f|X|f|f|C|J|f|K|f||||X|f|"Dell | EMC CX500 Disk Processor Enclosure Array (221-4205)"|f|f|N|f|X|f|X||f||f|1|NULL|NULL|NULL|f|X|7021|D||334111||f||f||E|||ONE DELL WAY|||ROUND ROCK|TX|786820001|USA|8779365180000|10|63500|TX|US||NULL||CDO|CDO|||||0||0.0|||4|D|NULL|f|f|f|f|f|f|||O||114315195|2005|DELL INC.|47|70|TX10|ZZ||||NULL|c||||20110114')

        self.assertEqual(0, Contract.objects.all().count())

        cursor = connections['default'].cursor()
        cursor.copy_from(input, 'contracts_contract', sep='|', null='NULL', columns=ContractsLoader().fields())

        self.assertEqual(1, Contract.objects.all().count())

    def assert_eq_ignoring_leading_trailing_space(self, expected, actual):
        self.maxDiff = None
        self.assertEqual(self.strip_lines(expected), self.strip_lines(actual))


    def strip_lines(self, values):
        if type(values) != type([]):
            values = values.split("\n")

        return [ x.strip() for x in values if re.search(r'[^ ]', x) ]



