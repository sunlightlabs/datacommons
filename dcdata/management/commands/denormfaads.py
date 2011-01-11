from dcdata.grants.models import Grant
from django.contrib.localflavor.us.us_states import STATES_NORMALIZED
from django.core.management.base import CommandError, BaseCommand
from optparse import make_option
from saucebrush import run_recipe
from saucebrush.emitters import Emitter, DebugEmitter, CSVEmitter
from saucebrush.filters import (
    Filter, FieldModifier, FieldRenamer, FieldRemover, UnicodeFilter
)
import os
import MySQLdb
import MySQLdb.cursors

def state_abbr(name):
    abbr = STATES_NORMALIZED.get(name.strip().lower(), None)
    return abbr or ''

class CountEmitter(Emitter):
    
    def __init__(self, every=1000):
        super(Emitter, self).__init__()
        self.every = every
        self.count = 0

    def emit_record(self, record):
        self.count += 1
        if self.count % self.every == 0:
            print "%s records" % self.count

class MySQLSource(object):
    
    def __init__(self, query, host, username, password, db):
        self.conn = MySQLdb.connect(
            host=host,
            user=username,
            passwd=password,
            db=db,
            cursorclass=MySQLdb.cursors.SSDictCursor)
        self.query = query
        
    def __iter__(self):
        cur = self.conn.cursor()
        cur.execute(self.query)
        for record in cur:
            yield record


class Command(BaseCommand):

    option_list = BaseCommand.option_list + (
        make_option("-c", "--host", dest="host", help="MySQL host", metavar="HOST"),
        make_option("-d", "--database", dest="database", help="MySQL database", metavar="DATABASE"),
        make_option("-o", "--outfile", dest="outfile", help="CSV output file", metavar="PATH"),
        make_option("-p", "--password", dest="password", help="MySQL password", metavar="PASSWORD"),
        make_option("-u", "--username", dest="username", help="MySQL username", metavar="USERNAME"),
        make_option("-y", "--year", dest="year", help="fiscal year to load", metavar="YEAR"),
    )

    def handle(self, *args, **options):

        for required in ('username','outfile'):
            if required not in options or options[required] is None:
                raise CommandError("%s argument is required" % required)

        outfile = os.path.abspath(options['outfile'])
        outfields = [field.name for field in Grant._meta.fields]
        
        query = """SELECT * FROM faads_main_april2010"""
        if options['year']:
            query = "%s WHERE fiscal_year = %s" % (query, options['year'])
        
        mysql_params = {
            'query': query,
            'db': options['database'] or 'faads',
            'username': options['username'],
            'password': options['password'] or '',
            'host': options['host'] or 'localhost',
        }
        
        run_recipe(
            MySQLSource(**mysql_params),
            FieldRemover(('lookup_parent_rec_id','fyq','fyq_correction','mod_name',
                          'recipient_cong_district','duns_conf_code',
                          'starting_date','ending_date')),
            FieldRenamer({
                'id':                       'record_id',
                'record_flag':              'rec_flag',
                'cfda_program_number':      'cfda_program_num',
                'state_application_id':     'sai_number',
                'recipient_id':             'recip_id',
                'recipient_city':           'recipient_city_name',
                'recipient_county':         'recipient_county_name',
                'recipient_state':          'recipient_state_name',
                'recipient_zipcode':        'recipient_zip',
                'recipient_district':       'recipient_cd',
                'recipient_category':       'recip_cat_type',
                'recipient_address1':       'receip_addr1',
                'recipient_address2':       'receip_addr2',
                'recipient_address3':       'receip_addr3',
                'recipient_duns':           'duns_no',
                'recipient_parent_duns':    'parent_duns_no',
                'action_date':              'obligation_action_date',
                'agency_category':          'maj_agency_cat',
                'amount_federal':           'fed_funding_amount',
                'amount_nonfederal':        'non_fed_funding_amount',
                'amount_total':             'total_funding_amount',
                'amount_loan':              'face_loan_guran',
                'amount_subsidy_cost':      'orig_sub_guran',
                'assistance_category':      'asst_cat_type',
                'correction':               'correction_late_ind',
                'place_code':               'principal_place_code',
                'place_state':              'principal_place_state',
                'place_state_code':         'principal_place_state_code',
                'place_city':               'principal_place_cc',
                'place_zipcode':            'principal_place_zip',
                'place_district':           'principal_place_cd',
                'psta_agency_code':         'progsrc_agen_code',
                'psta_account_code':        'progsrc_acnt_code',
                'psta_subaccount_code':     'progsrc_subacnt_code',
            }),
            FieldModifier(('recipient_state', 'place_state'), state_abbr),
            UnicodeFilter(),
            CountEmitter(every=10000),
            CSVEmitter(open(outfile, 'w'), fieldnames=outfields),
            #DebugEmitter(),
        )