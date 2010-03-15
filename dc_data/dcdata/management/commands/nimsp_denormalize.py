import hashlib
import inspect
import logging
import sys
import os
import re

import MySQLdb
import psycopg2

from dcdata.contribution.models import NIMSP_TRANSACTION_NAMESPACE

import saucebrush
from saucebrush.emitters import CSVEmitter, DebugEmitter
from saucebrush.sources import CSVSource
from saucebrush.filters import *

from dcdata.utils.dryrub import CountEmitter, VerifiedCSVSource,\
    CSVFieldVerifier

from scripts.nimsp.salt import DCIDFilter, SaltFilter

from settings import OTHER_DATABASES

from scripts.nimsp.common import CSV_SQL_MAPPING, SQL_DUMP_FILE
from dcdata.processor import chain_filters, load_data
from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
from dcdata.loading import model_fields
from dcdata.utils.sql import parse_decimal, parse_int


FIELDNAMES = model_fields('contribution.Contribution')

SALT_KEY = 'smokehouse'

zip5_re = re.compile("^\s*(?P<zip5>\d{5})(?:[- ]*\d{4})?(?!\d)")

def debug(record, message):
    try:
        logging.debug("%s:[%s] %s" % (inspect.stack()[1][3], record['contributionid'], message))
    except:
        logging.debug("%s:%s:%s" % (inspect.stack()[1][3], message, record))

def error(record, message):
    try:
        logging.error("%s:[%s] %s" % (inspect.stack()[1][3], record['contributionid'], message))
    except:
        logging.error("%s:%s:%s" % (inspect.stack()[1][3], message, record))

def warn(record, message):
    try:
        logging.warn("%s:[%s] %s" % (inspect.stack()[1][3], record['contributionid'], message))
    except:
        logging.warn("%s:%s:%s" % (inspect.stack()[1][3], message, record))



class FieldListFilter(Filter):
    """ A filter to limit fields to those in a list, and add empty values for missing fields. """
    def __init__(self, keys):
        super(FieldListFilter, self).__init__()
        self._target_keys = utils.str_or_list(keys)

    def process_record(self, record): 
        for key in record.keys():
            if key not in self._target_keys:
                del(record[key])
        for key in self._target_keys:
            if key not in record.keys():
                record[key] = None
        return record


class BestAvailableFilter(Filter):
    """ Merge contributor fields using best available value """
  
    def process_record(self, record):
        def nonempty(value):
            return value is not None and value != ''

        record['contributor_name'] = record['newcontributor'] if nonempty(record['newcontributor']) else record['contributor'] if nonempty(record['contributor']) else None 
        record['contributor_address'] = record['newaddress'] if nonempty(record['newaddress']) else record['address'] if nonempty(record['address']) else None
        record['contributor_employer'] = record['employer'] if nonempty(record['employer']) else None
        record['organization_name'] = record['newemployer'] if nonempty(record['newemployer']) else None

        for f in ('contributor','newcontributor','address','newaddress','employer','newemployer'):
            del(record[f])

        return record


class RecipientFilter(Filter):
    incumbent_map = {
        'I': True,
        'C': False,
        'O': False
        }
        
    def process_record(self, record):
        if record['committee_party'] and not record['recipient_party']: 
            record['recipient_party'] = record['committee_party']
        if record['recipient_party']:
            if record['recipient_party'] == 'P':
                record['recipient_party'] = None
        record['is_incumbent'] = self.incumbent_map.get(record['incumbent']) 
        return record

class SeatFilter(Filter):
    election_type_map = {
        'CL': 'C', # Utah candidate culling process 
        'L':  'G', # General
        'LR': 'R', # Judicial retention election (no opponents) 
        'PL': 'P', # Primary
        'W':  'G', # General
        'WR': 'R'  # Judicial retention
        }
    office_code_map = {
        'G': 'state:governor',
        'H': 'state:lower',
        'S': 'state:upper',
        'J': 'state:judicial',
        'K': 'state:judicial',
        'O': 'state:office'
        }

    def process_record(self, record):
        if record['district'] is not None:
            m = re.match("^0*(?P<district_number>[1-9]+\w*)", record['district'])
            if m:
                record['district'] = "%s-%s" % (record['seat_state'], m.group("district_number"))
            else:
                record['district'] = None # how to handle nonstandard districts?
        if record['seat'] is not None:
            record['seat'] = self.office_code_map.get(record['seat'])
        if record['status'] is not None:
            if record['status'].startswith('W') or record['status'].endswith('W'):
                record['seat_result'] = 'W'
            elif record['status'].startswith('L') or record['status'].endswith('L'):
                record['seat_result'] = 'L'
        record['election_type'] = self.election_type_map.get(record['status'])
        return record


class MultiFieldConversionFilter(Filter):
    
    def __init__(self, name_to_func):
        super(MultiFieldConversionFilter, self).__init__()
        self._name_to_func = name_to_func

    def process_record(self, record):
        for key in self._name_to_func.keys():
            if key in record:
                try:
                    record[key] = self._name_to_func[key](record[key])
                except:
                    warn(record, "Could not convert value '%s': %s" % (record[key], sys.exc_info()[0]))
                    record[key] = None
                    
        return record


class IdsFilter(Filter):

    def __init__(self):
        super(IdsFilter, self).__init__()

    def process_record(self,record):
        # Recipient
        if record['candidate_id'] and record['committee_id']:
            error(record, 'record has both candidate and committee ids. unhandled.')
            return record
        elif record['candidate_id']:
            record['recipient_type'] = 'politician'
            record['recipient_ext_id'] = record['unique_candidate_id'] if record['unique_candidate_id'] and record['unique_candidate_id'] not in ('', '0') else None
        elif record['committee_id']:
            record['recipient_type'] = 'committee'
            record['recipient_ext_id'] = record['committee_ext_id'] = record['committee_id']

        # Contributor
        if record['contributor_id']:
            record['contributor_ext_id'] = record['contributor_id']
            record['contributor_type'] = None
        if record['newemployerid']:
            record['organization_ext_id'] = record['newemployerid']
        if record['parentcompanyid']:
            record['parent_organization_ext_id'] = record['parentcompanyid']

        for f in ('candidate_id','committee_id','contributor_id','newemployerid','parentcompanyid'):
            del(record[f])

        return record

class ZipCleaner(Filter):
    def process_record(self, record):
        if record['contributor_zipcode']:
            if len(record['contributor_zipcode']) >= 5:
                m = zip5_re.match(record['contributor_zipcode'])
                if m:
                    record['contributor_zipcode'] = m.group('zip5')
                else:
                    record['contributor_zipcode'] = None 
            else:
                record['contributor_zipcode'] = None
        return record

class AllocatedEmitter(CSVEmitter):
    def emit_record(self, record):
        if record['contributor_category'] and record['contributor_category'].startswith('Z2'):
            pass # this is the condition we don't want!
        else:
            super(AllocatedEmitter, self).emit_record(record)

class UnallocatedEmitter(CSVEmitter):
    def emit_record(self, record):
        if record['contributor_category'] and record['contributor_category'].startswith('Z2'):
            super(UnallocatedEmitter, self).emit_record(record)


class NIMSPDenormalize(BaseCommand):
    
    option_list = BaseCommand.option_list + (
        make_option("-d", "--dataroot", dest="dataroot",
                      help="path to data directory", metavar="PATH"),
        make_option("-s", "--saltsdb", dest="saltsdb",
                    help="path to salts SQLite database", metavar="PATH"),
        make_option("-i", "--infile", dest="input_path",
                      help="path to input csv", metavar="FILE"))
    
    def handle(self, *args, **options):
        if 'dataroot' not in options:
            CommandError("path to dataroot is required")
        if 'saltsdb' not in options:
            CommandError("path to saltsdb is required")
    
        dataroot = os.path.abspath(options['dataroot'])
        assert dataroot
        if not os.path.exists(dataroot):
            print "No such directory %s" % dataroot
            sys.exit(1)
        saltsdb = os.path.abspath(options['saltsdb'])
        assert saltsdb
        if not os.path.exists(saltsdb):
            print "No such database %s" % saltsdb
            sys.exit(1)
        denorm_path = os.path.join(dataroot, 'denormalized')
        if not os.path.exists(denorm_path):
            os.makedirs(denorm_path)
        
        input_path = options.get('input_path', '') or os.path.join(denorm_path, SQL_DUMP_FILE)
        
#        con = self.mysql_connection() 
            
        self.process_allocated(denorm_path, input_path)
            
        self.process_unallocated(denorm_path, saltsdb)

    @staticmethod
    def get_allocated_record_processor():
        input_type_conversions = dict([(field, conversion_func) for (field, _, conversion_func) in CSV_SQL_MAPPING if conversion_func])
        
        return chain_filters(
            CSVFieldVerifier(),
            MultiFieldConversionFilter(input_type_conversions),

            # munge fields
            BestAvailableFilter(),
            RecipientFilter(),
            SeatFilter(),
            IdsFilter(),
            FieldModifier('date', lambda x: str(x) if x else None),
            ZipCleaner(),
           
            # add static fields
            FieldAdder('is_amendment',False),
            FieldAdder('transaction_namespace', NIMSP_TRANSACTION_NAMESPACE),

            FieldListFilter(FIELDNAMES + ['contributionid']))
    
    @staticmethod
    def process_allocated(denorm_path, input_path):
        
        # create allocated things
        allocated_csv_filename = os.path.join(denorm_path,'nimsp_allocated_contributions.csv')
        allocated_csv = open(os.path.join(denorm_path, allocated_csv_filename), 'w')
        allocated_emitter = AllocatedEmitter(allocated_csv, fieldnames=FIELDNAMES)
        
        # create unallocated things
        unallocated_csv_filename = os.path.join(denorm_path, 'nimsp_unallocated_contributions.csv.TMP')
        unallocated_csv = open(os.path.join(denorm_path, unallocated_csv_filename), 'w')
        unallocated_emitter = UnallocatedEmitter(unallocated_csv, fieldnames=FIELDNAMES + ['contributionid'])

        input_file = open(input_path, 'r')
        
        input_fields = [name for (name, _, _) in CSV_SQL_MAPPING]
 
        source = VerifiedCSVSource(input_file, input_fields)
    
        output_func = chain_filters(
            unallocated_emitter,
            DCIDFilter(SALT_KEY),
            allocated_emitter)
    
        load_data(source, NIMSPDenormalize.get_allocated_record_processor(), output_func)
    
        for o in [allocated_csv,unallocated_csv]:
            o.close()

    @staticmethod
    def get_unallocated_record_processor(salts_db):
        dcid = DCIDFilter(SALT_KEY)
        return chain_filters(        
            CSVFieldVerifier(),
            FieldModifier(['contributionid'], parse_int),
            FieldModifier(['amount'], parse_decimal),
            SaltFilter(100,salts_db,dcid),
            dcid)
    
    @staticmethod        
    def process_unallocated(denorm_path, salts_db):
        
        unallocated_csv_filename = os.path.join(denorm_path, 'nimsp_unallocated_contributions.csv.TMP')
        unallocated_csv = open(os.path.join(denorm_path, unallocated_csv_filename), 'r')
    
        salted_csv_filename = os.path.join(denorm_path, 'nimsp_unallocated_contributions.csv')
        salted_csv = open(salted_csv_filename, 'w')

        source = VerifiedCSVSource(unallocated_csv, fieldnames=FIELDNAMES + ['contributionid'], skiprows=1)

        output_func = CSVEmitter(salted_csv, FIELDNAMES).process_record
  
        load_data(source, NIMSPDenormalize.get_unallocated_record_processor(salts_db), output_func)
    
        for f in [salted_csv,unallocated_csv]:
            f.close()
    

Command = NIMSPDenormalize

