#!/usr/bin/env python

import csv
import inspect
import logging
import os
import sys
#from warnings import resetwarnings

import MySQLdb

import saucebrush
from saucebrush.emitters import CSVEmitter, DebugEmitter
from saucebrush.filters import *
from saucebrush.sources import CSVSource

from dcdata.utils.dryrub import CountEmitter

from salt import DCIDFilter, SaltFilter 


FIELDNAMES = ['id', 'import_reference', 'cycle', 'transaction_namespace', 'transaction_id', 'transaction_type', 'filing_id', 'is_amendment', 'amount', 'datestamp', 'contributor_name', 'contributor_urn', 'contributor_entity', 'contributor_type', 'contributor_occupation', 'contributor_employer', 'contributor_gender', 'contributor_address', 'contributor_city', 'contributor_state', 'contributor_zipcode', 'contributor_category', 'contributor_category_order', 'organization_name', 'organization_entity', 'parent_organization_name', 'parent_organization_entity', 'recipient_name', 'recipient_urn', 'recipient_entity', 'recipient_party', 'recipient_type', 'recipient_category', 'recipient_category_order', 'committee_name', 'committee_urn', 'committee_entity', 'committee_party', 'election_type', 'district', 'seat', 'seat_status', 'seat_result']


zip5_re = re.compile("^\s*(?P<zip5>\d{5})(?:[- ]*\d{4})?(?!\d)")

def debug(record, message):
    try:
        logging.error("%s:[%s] %s" % (inspect.stack()[1][3], record['contributionid'], message))
    except:
        logging.error("%s:%s:%s" % (inspect.stack()[1][3], message, record))

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
    #office_code_map = {
    #    'G': 'state:governor',
    #    'H': 'state:house',
    #    'S': 'state:senate',
    #    'J': 'state:judicial',
    #    'K': 'state:judicial',
    #    'O': 'state:office'
    #    }

    def process_record(self, record):
        if record['district'] is not None:
            record['district'] = re.sub("^0+(?:[1-9])","", record['district'])
            if len(record['district']) > 8:
                warn(record, "Bad or overlength district: %s" % record['district'])
                record['district'] = None
        #record['seat'] = self.office_code_map.get(record['officecode'])
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
            if len(record['contributor_zipcode']) >= 5:
                m = zip5_re.match(record['contributor_zipcode'])
                if m:
                    record['contributor_zipcode'] = m.group('zip5')
                else:
                    warn(record, "Bad zipcode: %s (%s)" % (record['contributor_zipcode'], record['contributor_state'] or 'NONE'))
                    record['contributor_zipcode'] = None 
            else:
                if record['contributor_zipcode'] not in ('-','N/A','N.A.','UNK','UNKNOWN'):
                    warn(record, "Bad zipcode: %s (%s)" % (record['contributor_zipcode'], record['contributor_state'] or 'NONE'))
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


# urn methods

def committee_urn(s):
    return 'urn:nimsp:committee:%d' % s if s else None

def contributor_urn(s):
    return 'urn:nimsp:contributor:%d' % s if s else None

def organization_urn(s):
    return 'urn:nimsp:organization:%d' % s if s else None
       
def recipient_urn(s):
    return 'urn:nimsp:candidate:%d' % s if s else None

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
    parser.add_option("-v", "--verbose", action='store_false', dest="verbose", default=False,
                      help="noisy output")

    (options, args) = parser.parse_args()

    if not options.dataroot:
        parser.error("path to dataroot is required")

    dataroot = os.path.abspath(options.dataroot)
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
    
    con = MySQLdb.connect(db='nimsp', user='datacommons', host='localhost', passwd='vitamind')
    cur = con.cursor(MySQLdb.cursors.DictCursor)
    
    #Contributions
    stmt = """
select ContributionID as contributionid,Amount as amount,Date as datestamp,Contributor as contributor,NewContributor as newcontributor,Occupation as occupation,Employer as employer,NewEmployer as newemployer,ParentCompany as parentcompany,ContributorOwner as contributorowner,PACName as pacname,Address as address,NewAddress as newaddress,City as contributor_city,State as contributor_state,ZipCode as contributor_zipcode,c.CatCode as contributor_category,NewContributorID as contributor_id,NewEmployerID as newemployerid,ParentCompanyID as parentcompanyid,ContributionsTimestamp as contributionstimestamp,c.RecipientReportsBundleID as recipientreportsbundleid,
   r.RecipientID as recipientid, r.CandidateID as candidate_id, r.CommitteeID as committee_id, r.RecipientName as recipient_name,
   syr.Yearcode as cycle,
   os.District as district,
   cand.Status as status, cand.ICO as incumbent,
   oc.OfficeType as seat,
   p_cand.PartyType as recipient_party,
   p_comm.PartyType as committee_party,
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

        # merge fields using first available 
        FieldMerger({'contributor_name': ('newcontributor','contributor', 'first','last')}, lambda nc,c,f,l: nc if (nc is not None and nc != "") else c if (c is not None and c != "") else ("%s %s" % [f,l]).strip() if (f is not None and f != "" and l is not None and l != "") else None),
        FieldMerger({'contributor_address': ('newaddress','address')}, lambda x,y: x if (x is not None and x != "") else y if (y is not None and y != "") else None),
        FieldMerger({'contributor_employer': ('newemployer','employer')}, lambda x,y: x if (x is not None and x != "") else y if (y is not None and y != "") else None),
        FieldMerger({'organization_name': ('newemployer','employer')}, lambda x,y: x if (x is not None and x != "") else y if (y is not None and y != "") else None),
        
        #OrganizationFilter(),
        RecipientFilter(),
        SeatFilter(),
        
        # create URNs
        FieldMerger({'committee_urn': ('committee_id',)}, committee_urn),
        FieldMerger({'contributor_urn': ('contributor_id',)}, contributor_urn),
        FieldMerger({'organization_urn': ('newemployerid',)}, organization_urn),
        FieldMerger({'parent_organization_urn': ('parentcompanyid',)}, organization_urn),
        FieldMerger({'recipient_urn': ('candidate_id',)}, recipient_urn),
        
        # munge fields       
        FieldModifier('datestamp', lambda x: str(x) if x else None),
        ZipCleaner(),
            
        # add static fields
        FieldAdder('is_amendment',False),
        FieldAdder('transaction_namespace', 'urn:nimsp:transaction'),
        #FieldAdder('jurisdiction','S'),

        FieldListFilter(FIELDNAMES + ['contributionid']),
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

    saucebrush.run_recipe(
        CSVSource(unallocated_csv, fieldnames=FIELDNAMES + ['contributionid'], skiprows=1),
        
        IntFilter('contributionid'),
        FloatFilter('amount'),
        
        FieldAdder('salted',False),
        SaltFilter(rando=100),
        DCIDFilter(),

        CountEmitter(every=2000),
        unsalted_emitter,
        salted_emitter
        )

    for f in [salted_csv,unsalted_csv,unallocated_csv]:
        f.close()


if __name__ == "__main__":

    logging.basicConfig(level=logging.DEBUG)

    main()
