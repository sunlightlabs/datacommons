#!/usr/bin/env python

import csv
import hashlib
import inspect
import logging
import os
import string
import sys

import ConfigParser
import MySQLdb
import psycopg2

import saucebrush
from saucebrush.emitters import CSVEmitter, DebugEmitter
from saucebrush.filters import *
from saucebrush.sources import CSVSource

from dcdata.utils.dryrub import CountEmitter, NullEmitter
from dcdata.utils.name_patterns import first_name_pat, last_name_pat

from salt import DCIDFilter, SaltFilter

from settings import OTHER_DATABASES

FIELDNAMES = ['id', 'import_reference', 'cycle', 'transaction_namespace', 'transaction_id', 'transaction_type', 'filing_id', 'is_amendment', 'amount', 'datestamp', 'contributor_name', 'contributor_urn', 'contributor_entity', 'contributor_type', 'contributor_occupation', 'contributor_employer', 'contributor_gender', 'contributor_address', 'contributor_city', 'contributor_state', 'contributor_zipcode', 'contributor_category', 'contributor_category_order', 'organization_name', 'organization_entity', 'parent_organization_name', 'parent_organization_entity', 'recipient_name', 'recipient_urn', 'recipient_entity', 'recipient_party', 'recipient_type', 'recipient_category', 'recipient_category_order', 'committee_name', 'committee_urn', 'committee_entity', 'committee_party', 'election_type', 'district', 'seat', 'seat_status', 'seat_result']


committee_words_re = re.compile('(?:\\b(?:' + '|'.join(['CMTE','COMMITTEE','FRIENDS','PAC','UNION']) + '))' )
first_name_re = re.compile(first_name_pat + '\\b')
last_name_re = re.compile(last_name_pat + '\\b')
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

class ChunkedSqlSource(object):
    """ Saucebrush source for reading from a database DictCursor.

        The data is fetched in chunks for memory management.
        
        For postgres, use psycopg2.extras.RealDictCursor.
    """
    def make_stmt(self,offset):
        return self.stmt + " limit %d offset %d" % (self.chunk, offset)
        
    def __init__(self, dict_cur, stmt, chunk=10000, limit=None):
        self.cur = dict_cur
        self.chunk = int(chunk)
        if limit:
            self.limit = int(limit)
        else:
            self.limit = None
        self.offset = 0
        self.stmt = stmt

    def fetchsome(self):
        done = False       
        while not done:
            self.cur.execute(self.make_stmt(self.offset))
            results = self.cur.fetchall()
            if results == []:
                done = True
            elif len(results) < self.chunk:
                done = True
            for result in results:
                self.offset += 1
                if self.limit and (self.offset > self.limit):
                    done = True
                    break
                yield result

    def __iter__(self):
        return self.fetchsome()

class FloatFilter(FieldFilter):
    def __init__(self, field, on_error=None):
        super(FloatFilter, self).__init__(field)
        self._on_error = on_error
    def process_field(self, item):
        try:
            return float(item)
        except ValueError:
            return self._on_error

class IntFilter(FieldFilter):
    def __init__(self, field, on_error=None):
        super(IntFilter, self).__init__(field)
        self._on_error = on_error
    def process_field(self, item):
        try:
            return int(item)
        except ValueError:
            return self._on_error

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

class ContributorTypeFilter(Filter):
    def process_record(self,record):
        """ Try to distinguish individuals from committees"""
        individual = 0
        committee = 0
        if record['first'] and record['first'] != '' and record['last'] and record['last'] != '':
            if first_name_re.match(record['first']) and last_name_re.match(record['last']):
                individual += 5
            individual -= string.count(record['first'], ' ')
        if record['pacname'] and record['pacname'] != '':
            committee += 1
        for f in ['contributor', 'contributor_occupation', 'first']:
            if record[f] and record[f] != '' and committee_words_re.search(record[f]):
                committee += 1
        if record['contributor_id'] and record['newemployerid'] and record['contributor_id'] == record['newemployerid']:
            committee += 1
        if individual > 0 and individual > committee:          
            record['contributor_type'] = 'individual'
        elif committee > 0 and committee > individual:
            record['contributor_type'] = 'committee'
        else:
            record['contributor_type'] = None
        return record
        

class EmployerOccupationFilter(Filter):
        
    def process_record(self, record):
        for f in ('contributor_occupation','contributor_employer'):
            if record[f]:
                if len(record[f]) > 64:
                    record[f] = record[f][:63]
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

class UrnFilter(Filter):

    def process_record(self,record):
        contributor_type_map = {'individual':'individual', 'committee':'committee', '': 'contributor', None: 'contributor'}

        if record['candidate_id'] and record['committee_id']:
            warn('record has both candidate and committee ids. unhandled.', record)
            return record
        elif record['candidate_id']:
            record['recipient_type'] = 'candidate'
            record['recipient_urn'] = 'urn:nimsp:candidate:%d' % record['candidate_id']
            record['recipient_entity'] = hashlib.md5(record['recipient_urn']).hexdigest()
        elif record['committee_id']:
            record['recipient_type'] = 'committee'
            record['recipient_urn'] = record['committee_urn'] = 'urn:nimsp:committee:%d' % record['committee_id']
            record['recipient_entity'] = record['committee_entity'] = hashlib.md5(record['committee_urn']).hexdigest()
        if record['contributor_id']:
            if record['contributor_id'] == record['newemployerid'] and (record['contributor_type'] is None or record['contributor_type'] == 'committee'):
                # contributor is an organization which is probably really a business pac?
                record['contributor_urn'] = 'urn:nimsp:%s:%d' % ('contributor', record['contributor_id'])
                if record['contributor_occupation'] and record['contributor_occupation'] != '':
                    # occupation would be kind of fake
                    debug(record,"Overloaded occupation \"%s\" because contributor is an organization" % record['contributor_occupation'])
            else:
                record['contributor_urn'] = 'urn:nimsp:%s:%d' % ('contributor', record['contributor_id'])
            record['contributor_entity'] = hashlib.md5(record['contributor_urn']).hexdigest()
        elif record['contributor_name'] and record['contributor_name'] != '':
            record['contributor_urn'] = 'urn:nimsp:%s:%s' % (contributor_type_map.get(record['contributor_id']), record['contributor_name'].strip())
            record['contributor_entity'] = hashlib.md5(record['contributor_urn']).hexdigest()
        if record['newemployerid']:
            record['organization_urn'] = 'urn:nimsp:organization:%d' % record['newemployerid']
            record['organization_entity'] = hashlib.md5(record['organization_urn']).hexdigest()
        elif record['organization_name'] and record['organization_name'] != '':
            record['organization_urn'] = 'urn:nimsp:organization:%s' % record['organization_name'].strip()
            record['organization_entity'] = hashlib.md5(record['organization_urn']).hexdigest()
        if record['parentcompanyid']:
            record['parent_organization_urn'] = 'urn:nimsp:organization:%d' % record['parentcompanyid']
            record['parent_organization_entity'] = hashlib.md5(record['parent_organization_urn']).hexdigest()
        elif record['parent_organization_name'] and record['parent_organization_name'] != '':
            record['parent_organization_urn'] = 'urn:nimsp:organization:%s' % record['parent_organization_name'].strip()
            record['parent_organization_entity'] = hashlib.md5(record['parent_organization_urn']).hexdigest()

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
                    debug(record, "Bad zipcode: %s (%s)" % (record['contributor_zipcode'], record['contributor_state'] or 'NONE'))
                    record['contributor_zipcode'] = None 
            else:
                if record['contributor_zipcode'] not in ('-','N/A','N.A.','NONE','UNK','UNKNOWN'):
                    debug(record, "Bad zipcode: %s (%s)" % (record['contributor_zipcode'], record['contributor_state'] or 'NONE'))
                record['contributor_zipcode'] = None
        return record

class AllocatedEmitter(CSVEmitter):
    def emit_record(self, record):
        if record['contributor_category'] and not record['contributor_category'].startswith('Z2'):
            super(AllocatedEmitter, self).emit_record(record)

class UnallocatedEmitter(CSVEmitter):
    def emit_record(self, record):
        if record['contributor_category'] and record['contributor_category'].startswith('Z2'):
            super(UnallocatedEmitter, self).emit_record(record)

class SaltedEmitter(CSVEmitter):
    def emit_record(self, record):
        if 'salted' in record and record['salted']:
            del(record['salted'])
            super(SaltedEmitter, self).emit_record(record)

class UnsaltedEmitter(CSVEmitter):
    def emit_record(self, record):
        if 'salted' in record and not record['salted']:
            del(record['salted'])
            super(UnsaltedEmitter, self).emit_record(record)

def main():

    from optparse import OptionParser

    usage = "usage: %prog --dataroot DIR [options]"

    parser = OptionParser(usage=usage)
    parser.add_option("-c", "--cycle", dest="cycle", metavar='YYYY',
                      help="cycle to process (default all)")
    parser.add_option("-d", "--dataroot", dest="dataroot",
                      help="path to data directory", metavar="PATH")
    parser.add_option("-n", "--number", dest="n", metavar='ROWS',
                      help="number of rows to process")
    parser.add_option("-v", "--verbose", action='store_true', dest="verbose", 
                      help="noisy output")

    (options, args) = parser.parse_args()

    if not options.dataroot:
        parser.error("path to dataroot is required")


    dataroot = os.path.abspath(options.dataroot)
    if not os.path.exists(dataroot):
        print "No such directory %s" % dataroot
        sys.exit(1)
    tmppath = os.path.join(dataroot, 'tmp')
    if not os.path.exists(tmppath):
        os.makedirs(tmppath)
    
    n = options.n if options.n else None

    allocated_csv_filename = os.path.join(tmppath,'nimsp_allocated_contributions_%s.csv' % options.cycle if options.cycle else 'nimsp_allocated_contributions.csv')
    unallocated_csv_filename = os.path.join(tmppath, 'nimsp_unallocated_contributions_%s.csv.TMP' % options.cycle if options.cycle else 'nimsp_unallocated_contributions.csv.TMP')

    allocated_csv = open(os.path.join(tmppath, allocated_csv_filename), 'w')
    unallocated_csv = open(os.path.join(tmppath, unallocated_csv_filename), 'w')
    
    allocated_emitter = AllocatedEmitter(allocated_csv, fieldnames=FIELDNAMES)
    unallocated_emitter = UnallocatedEmitter(unallocated_csv, fieldnames=FIELDNAMES + ['contributionid'])

    try:
        con = MySQLdb.connect(
            db=OTHER_DATABASES['nimsp']['DATABASE_NAME'],
            user=OTHER_DATABASES['nimsp']['DATABASE_USER'],
            host=OTHER_DATABASES['nimsp']['DATABASE_HOST'] if 'DATABASE_HOST' in OTHER_DATABASES['nimsp'] else 'localhost',
            passwd=OTHER_DATABASES['nimsp']['DATABASE_PASSWORD'],
            )
        cur = con.cursor(MySQLdb.cursors.DictCursor)
    except Exception, e:
        print "Unable to connect to nimso database: %s" % e 
        sys.exit(1)
    
  
    
    #Contributions
    stmt = """
select c.ContributionID as contributionid,c.Amount as amount,c.Date as datestamp,c.Contributor as contributor,c.NewContributor as newcontributor,c.First as first,c.Last as last,c.Occupation as contributor_occupation,c.Employer as employer,c.NewEmployer as newemployer,c.ParentCompany as parent_organization_name,c.ContributorOwner as contributorowner,c.PACName as pacname,c.Address as address,c.NewAddress as newaddress,c.City as contributor_city,c.State as contributor_state,c.ZipCode as contributor_zipcode,c.CatCode as contributor_category,c.NewContributorID as contributor_id,c.NewEmployerID as newemployerid,c.ParentCompanyID as parentcompanyid,c.ContributionsTimestamp as contributionstimestamp,c.RecipientReportsBundleID as recipientreportsbundleid,
   r.RecipientID as recipientid, r.CandidateID as candidate_id, r.CommitteeID as committee_id, r.RecipientName as recipient_name,
   syr.Yearcode as cycle,
   os.StateCode as seat_state, os.District as district,
   cand.Status as status, cand.ICO as incumbent,
   oc.OfficeType as seat,
   p_cand.PartyType as recipient_party,
   p_comm.PartyType as committee_party,
   comm.CommitteeName as committee_name,
   cc.IndustryCode as contributor_industry
   from Contributions c
   left outer join RecipientReportsBundle rrb on c.RecipientReportsBundleID = rrb.RecipientReportsBundleID
   left outer join Recipients r on rrb.RecipientID = r.RecipientID
   left outer join StateYearReports syr on rrb.StateYearReportsID = syr.StateYearReportsID
   left outer join Candidates cand on r.CandidateID = cand.CandidateID
   left outer join OfficeSeats os on cand.OfficeSeatID = os.OfficeSeatID
   left outer join OfficeCodes oc on os.OfficeCode = oc.OfficeCode
   left outer join Committees comm on r.CommitteeID = comm.CommitteeID
   left outer join CatCodes cc on c.CatCode = cc.CatCode
   left outer join PartyLookup p_cand on cand.PartyLookupID = p_cand.PartyLookupID
   left outer join PartyLookup p_comm on comm.PartyLookupID = p_comm.PartyLookupID%s""" % ("\n   where syr.Yearcode = %s" % options.cycle if options.cycle else "")

    recipe = saucebrush.run_recipe(
        ChunkedSqlSource(cur,stmt,limit=n),
        ContributorTypeFilter(),

        # merge fields using first available 
        FieldMerger({'contributor_name': ('newcontributor','contributor', 'first','last')}, lambda nc,c,f,l: nc if (nc is not None and nc != "") else c if (c is not None and c != "") else ("%s %s" % [f,l]).strip() if (f is not None and f != "" and l is not None and l != "") else None),
        FieldMerger({'contributor_address': ('newaddress','address')}, lambda x,y: x if (x is not None and x != "") else y if (y is not None and y != "") else None),
        FieldMerger({'contributor_employer': ('employer','newemployer')}, lambda x,y: x if (x is not None and x != "") else y if (y is not None and y != "") else None),
        FieldMerger({'organization_name': ('employer','newemployer')}, lambda x,y: x if (x is not None and x != "") else y if (y is not None and y != "") else None),

        # munge fields       
        EmployerOccupationFilter(),
        RecipientFilter(),
        SeatFilter(),
        UrnFilter(),
        FieldModifier('datestamp', lambda x: str(x) if x else None),
        ZipCleaner(),
            
        # add static fields
        FieldAdder('is_amendment',False),
        FieldAdder('transaction_namespace', 'urn:nimsp:transaction'),

        FieldListFilter(FIELDNAMES + ['contributionid']),
        #DebugEmitter(),
        CountEmitter(every=2000),
        unallocated_emitter,
        DCIDFilter(),
        allocated_emitter,
        )
    for o in [allocated_csv,unallocated_csv,cur,con]:
        o.close()

    salted_csv_filename = os.path.join(tmppath, 'nimsp_unallocated_contributions_salted_%s.csv' % options.cycle if options.cycle else 'nimsp_unallocated_contributions_salted.csv')
    unsalted_csv_filename = os.path.join(tmppath, 'nimsp_unallocated_contributions_unsalted_%s.csv' % options.cycle if options.cycle else 'nimsp_unallocated_contributions_unsalted.csv')

    unallocated_csv = open(os.path.join(tmppath, unallocated_csv_filename), 'r')
    salted_csv = open(salted_csv_filename, 'w')
    unsalted_csv = open(unsalted_csv_filename, 'w')

    salted_emitter = SaltedEmitter(salted_csv, FIELDNAMES)
    unsalted_emitter = UnsaltedEmitter(unsalted_csv, FIELDNAMES)

    try:
        pcon = psycopg2.connect("dbname='%s' user='%s' host='%s' password='%s'" % (
            OTHER_DATABASES['salts']['DATABASE_NAME'],
            OTHER_DATABASES['salts']['DATABASE_USER'],
            OTHER_DATABASES['salts']['DATABASE_HOST'] if 'DATABASE_HOST' in OTHER_DATABASES['salts'] else 'localhost',
            OTHER_DATABASES['salts']['DATABASE_PASSWORD'],
            ))
    except Exception, e:
        print "Unable to connect to salts database: %s" %  e
        sys.exit(1)

    try:
        mcon = MySQLdb.connect(
            db=OTHER_DATABASES['nimsp']['DATABASE_NAME'],
            user=OTHER_DATABASES['nimsp']['DATABASE_USER'],
            host=OTHER_DATABASES['nimsp']['DATABASE_HOST'] if 'DATABASE_HOST' in OTHER_DATABASES['nimsp'] else 'localhost',
            passwd=OTHER_DATABASES['nimsp']['DATABASE_PASSWORD'],
            )
    except Exception, e:
        print "Unable to connect to nimsp database: %s" % e 
        sys.exit(1)
  
    salt_filter = SaltFilter(100,pcon,mcon)

    saucebrush.run_recipe(
        CSVSource(unallocated_csv, fieldnames=FIELDNAMES + ['contributionid'], skiprows=1),
        
        IntFilter('contributionid'),
        FloatFilter('amount'),
        
        FieldAdder('salted',False),
        salt_filter,
        DCIDFilter(),

        #DebugEmitter(),
        CountEmitter(every=2000),

        unsalted_emitter,
        salted_emitter
        )

    for f in [salted_csv,unsalted_csv,unallocated_csv, pcon, mcon]:
        f.close()


if __name__ == "__main__":
    main()
