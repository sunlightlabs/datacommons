#!/usr/bin/env python

import csv
import inspect
import logging
import os
#from warnings import resetwarnings

import MySQLdb

import saucebrush
from saucebrush.emitters import CSVEmitter, DebugEmitter
from saucebrush.filters import *


FIELDNAMES = ['id', 'import_reference', 'cycle', 'transaction_namespace', 'transaction_id', 'transaction_type',
              'filing_id', 'is_amendment', 'amount', 'datestamp', 'contributor_name', 'contributor_urn',
              'contributor_entity', 'contributor_type', 'contributor_occupation', 'contributor_employer',
              'contributor_gender', 'contributor_address', 'contributor_city', 'contributor_state',
              'contributor_zipcode', 'contributor_category', 'contributor_category_order',
              'organization_name', 'organization_entity', 'parent_organization_name',
              'parent_organization_entity', 'recipient_name', 'recipient_urn', 'recipient_entity',
              'recipient_party', 'recipient_type', 'recipient_category', 'recipient_category_order',
              'committee_name', 'committee_urn', 'committee_entity',
              'committee_party', 'election_type', 'district', 'seat', 'seat_status',
              'seat_result',]

zip5_re = re.compile("^(?P<zip5>\d{5})(?:[- ]*\d{4})?(?!\d)")

def debug(record, message):
    try:
        logging.error("%s:[%s] %s" % (inspect.stack()[1][3], record['transaction_id'], message))
    except:
        logging.error("%s:%s:%s" % (inspect.stack()[1][3], message, record))

def error(record, message):
    try:
        logging.error("%s:[%s] %s" % (inspect.stack()[1][3], record['transaction_id'], message))
    except:
        logging.error("%s:%s:%s" % (inspect.stack()[1][3], message, record))

def warn(record, message):
    try:
        logging.warn("%s:[%s] %s" % (inspect.stack()[1][3], record['transaction_id'], message))
    except:
        logging.warn("%s:%s:%s" % (inspect.stack()[1][3], message, record))

class CatCodeFilter(Filter):    
    def __init__(self, csvpath, fieldname='real_code'):        
        self._fieldname = fieldname
        
        # load catcodes        
        logging.debug('Loading catcodes from %s' % csvpath)
        
        self._catcodes = { }
        csvfile = open(csvpath)
        reader = csv.DictReader(csvfile, delimiter='\t')
        for record in reader:
            self._catcodes[record['catcode']] = record
        csvfile.close()        
        logging.debug('Finished loading catcodes')

    def process_record(self, record): 
        if record['catcode']:
            lookup = self._catcodes.get(record['catcode'])
            if lookup:               
                for f in ('contributor_category','contributor_industry','contributor_sector','transaction_type'):
                    record[f] = lookup.get(f)
                return record
            else:
                record['catcode'] = '%d' % record['catcode']
                warn(record, "Don't know industry,sector,transaction_type lookup for catcode %s" % (record['catcode']))

        return record

class ChunkedSqlSource(object):
    """ Saucebrush source for reading from a database DictCursor.

        The data is fetched in chunks for memory management.
        
        For postgres, use psycopg2.extras.RealDictCursor.
    """
    def make_stmt(self,offset):
        return self.stmt + " limit %d offset %d" % (self.chunk,offset)
        
    def __init__(self, dict_cur, stmt, chunk=10000, limit=None):
        self.cur = dict_cur
        self.chunk = chunk
        self.limit = limit 
        self.offset = 0
        self.stmt = stmt 

    def fetchsome(self):
        done = False       
        while not done:
            #resetwarnings
            self.cur.execute(self.make_stmt(self.offset))
            results = self.cur.fetchall()
            if results == []:
                done = True
            elif len(results) < self.chunk:
                done = True
            for result in results:
                self.offset += 1
                if self.limit and self.offset > self.limit:
                    done = True
                else:
                    yield result

    def __iter__(self):
        return self.fetchsome()

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

#class OrganizationFilter(Filter):
#    def process_record(self, record):
#        orgname = record.get('org_name', '').strip()
#        if not orgname:
#            orgname = record.get('emp_ef', '').strip()
#            if not orgname and '/' in record['fec_occ_emp']:
#                (emp, occ) = record['fec_occ_emp'].split('/', 1)
#                orgname = emp.strip()
#        record['organization_name'] = orgname or None
#        return record

class RecipientFilter(Filter):
    incumbent_map = {
        'I': True,
        'C': False,
        'O': False
        }
        
    def process_record(self, record):
        if record['recipient_party']:
            if record['recipient_party'] == 'P':
                record['recipient_party'] = None
        record['is_incumbent'] = self.incumbent_map.get(record['incumbent']) 
        return record

class SeatFilter(Filter):
    election_type_map = {
        'CL': 'candidate', # Utah candidate culling process 
        'L':  'general',
        'LR': 'retention', # Judicial retention election (no opponents) 
        'PL': 'primary',
        'W':  'general',
        'WR': 'retention'
        }
    office_code_map = {
        'G': 'state:governor',
        'H': 'state:house',
        'S': 'state:senate',
        'J': 'state:judicial',
        'K': 'state:judicial',
        'O': 'state:office'
        }

    def process_record(self, record):
        if record['district']:
            record['district'] = re.sub("^0+(?:[1-9])","", record['district'])
            if len(record['district']) > 8:
                record['district'] = None
                warn(record, "Bad district: %s" % record['district'])
        record['seat'] = self.office_code_map.get(record['officecode'])
        if record['status'] is not None:
            if record['status'].startswith('W') or record['status'].endswith('W'):
                record['seat_result'] = 'W'
            elif record['status'].startswith('L') or record['status'].endswith('L'):
                record['seat_result'] = 'L'
        record['election_type'] = self.election_type_map.get(record['status'])
        return record

class ZipCleaner(Filter):
    def process_record(self, record):
        if record['contributor_zipcode']:
            if len(record['contributor_zipcode']) in (5,9,10):
                m = zip5_re.match(record['contributor_zipcode'])
                if m:
                    record['contributor_zipcode'] = m.group('zip5')
                else:
                    warn(record, "Bad zipcode: %s (%s)" % (record['contributor_zipcode'], record['contributor_state'] or 'NONE'))
                    record['contributor_zipcode'] = None 
            else:
                if record['contributor_zipcode'] not in ('-','N/A','N.A.'):
                    warn(record, "Bad zipcode length: %s (%s)" % (record['contributor_zipcode'], record['contributor_state'] or 'NONE'))
                record['contributor_zipcode'] = None
        return record

def main():

    from optparse import OptionParser

    usage = "usage: %prog --dataroot DIR [options]"

    parser = OptionParser(usage=usage)
    parser.add_option("-d", "--dataroot", dest="dataroot",
                      help="path to data directory", metavar="PATH")
    parser.add_option("-n", "--number", dest="n",
                      help="number of records to load")
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose", default=False,
                      help="noisy output")

    (options, args) = parser.parse_args()

    if not options.dataroot:
        parser.error("path to dataroot is required")

    dataroot = os.path.abspath(options.dataroot)
    tmppath = os.path.join(dataroot, 'tmp')
    if not os.path.exists(tmppath):
        os.makedirs(tmppath)
    n = options.n if options.n else None

    emitter = CSVEmitter(open(os.path.join(tmppath, 'denormalize_nimsp.csv'), 'w'), fieldnames=FIELDNAMES)

    con = MySQLdb.connect(db='nimsp', user='root', host='localhost', passwd='vitamind')
    cur = con.cursor(MySQLdb.cursors.DictCursor)

    # urn methods

    def committee_urn(s):
        return 'urn:nimsp:committee:%d' % s if s else None

    def contributor_urn(s):
        return 'urn:nimsp:contributor:%d' % s if s else None

    def organization_urn(s):
        return 'urn:nimsp:organization:%d' % s if s else None
    
    
    def recipient_urn(s):
        return 'urn:nimsp:candidate:%d' % s if s else None
    
    #Contributions
    stmt = """
select ContributionID as transaction_id,Amount as amount,Date as datestamp,Contributor as contributor,NewContributor as newcontributor,Occupation as occupation,Employer as employer,NewEmployer as newemployer,ParentCompany as parentcompany,ContributorOwner as contributorowner,PACName as pacname,Address as address,NewAddress as newaddress,City as contributor_city,State as contributor_state,ZipCode as contributor_zipcode,CatCode as catcode,NewContributorID as contributor_id,NewEmployerID as newemployerid,ParentCompanyID as parentcompanyid,ContributionsTimestamp as contributionstimestamp,c.RecipientReportsBundleID as recipientreportsbundleid,
   r.RecipientID as recipientid, r.CandidateID as candidate_id, r.CommitteeID as committee_id, r.RecipientName as recipient_name,
   syr.Yearcode as cycle,
   cand.OfficeCode as officecode, cand.District as district, cand.Status as status, cand.ICO as incumbent,
   p_cand.PartyType as recipient_party,
   p_comm.PartyType as committee_party
   from Contributions c
   left outer join RecipientReportsBundle rrb on c.RecipientReportsBundleID = rrb.RecipientReportsBundleID
   left outer join Recipients r on rrb.RecipientID = r.RecipientID
   left outer join StateYearReports syr on rrb.StateYearReportsID = syr.StateYearReportsID
   left outer join Candidates cand on r.CandidateID = cand.CandidateID
   left outer join Committees comm on r.CommitteeID = comm.CommitteeID
   left outer join PartyLookup p_cand on cand.PartyLookupID = p_cand.PartyLookupID
   left outer join PartyLookup p_comm on comm.PartyLookupID = p_comm.PartyLookupID"""

    recipe = saucebrush.run_recipe(
        ChunkedSqlSource(cur,stmt,limit=n),
        #DebugEmitter(),

        # merge fields using first available 
        FieldMerger({'contributor_name': ('newcontributor','contributor', 'first','last')}, lambda nc,c,f,l: nc if (nc is not None and nc != "") else c if (c is not None and c != "") else ("%s %s" % [f,l]).strip() if (f is not None and f != "" and l is not None and l != "") else None),
        FieldMerger({'contributor_address': ('newaddress','address')}, lambda x,y: x if (x is not None and x != "") else y if  (y is not None and y != "") else None),
        FieldMerger({'contributor_employer': ('newemployer','employer')}, lambda x,y: x if (x is not None and x != "") else y if (y is not None and y != "") else None),
        FieldMerger({'organization_name': ('newemployer','employer')}, lambda x,y: x if (x is not None and x != "") else y if (y is not None and y != "") else None),

        #OrganizationFilter(),
        RecipientFilter(),
        SeatFilter(),
        CatCodeFilter(dataroot + '/catcodes.txt'),

        # create URNs
        FieldMerger({'committee_urn': ('committee_id',)}, committee_urn),
        FieldMerger({'contributor_urn': ('contributor_id',)}, contributor_urn),
        FieldMerger({'organization_urn': ('newemployerid',)}, organization_urn),
        FieldMerger({'parent_organization_urn': ('parentcompanyid',)}, organization_urn),
        FieldMerger({'recipient_urn': ('candidate_id',)}, recipient_urn),

        # munge fields       
        FieldModifier('transaction_id', lambda x: "nimsp:%d" % x),
        FieldModifier('datestamp', lambda x: str(x) if x else None),
        ZipCleaner(),

        # add static fields
        FieldAdder('is_amendment',False),
        FieldAdder('transaction_namespace', 'urn:nimsp:transaction'),
        #FieldAdder('jurisdiction','S'),

        FieldListFilter(FIELDNAMES),
        #DebugEmitter(), 
        emitter,      
    )
    #print recipe.rejected


if __name__ == "__main__":

    logging.basicConfig(level=logging.DEBUG)

    main()
