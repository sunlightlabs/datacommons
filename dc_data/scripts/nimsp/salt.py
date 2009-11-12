#!/usr/bin/env python
from datacommons import settings
from datacommons.sources.nimsp import FILE_TYPES
from datacommons.utils.dryrub import CountEmitter
from saucebrush.sources import CSVSource
from saucebrush.filters import Filter, FieldFilter, ConditionalFilter, FieldAdder, YieldFilter, FieldModifier
from saucebrush.emitters import CSVEmitter
import saucebrush
import csv
import random
import logging
import datetime
import psycopg2
from psycopg2 import extras

#############################################################

def connection_string(dbname, user, password=None, host=None, port=None, options=None):
    """ 
        A convenience function for getting a psycopg2 dns connection
        string from django settings
    """
    
    if options is None:
        options = { }
    
    try:
        
        from django.conf import settings
        
        if settings.DATABASE_ENGINE == 'postgresql_psycopg2':
            
            if dbname is None:
                dbname = getattr(settings, 'DATABASE_NAME', None)
            
            if user is None:
                user = getattr(settings, 'DATABASE_USER', None)
                        
            if password is None:
                password = getattr(settings, 'DATABASE_PASSWORD', None)
                
            if host is None:
                host = getattr(settings, 'DATABASE_HOST', None)
                
            if port is None:
                port = getattr(settings, 'DATABASE_PORT', None)
            
            if settings.DATABASE_OPTIONS:
                for (k,v) in settings.DATABASE_OPTIONS.items():
                    if k not in options.keys():
                        options[k] = v
                        
    except ImportError:
        pass
        
    params = options.copy()
        
    params['dbname'] = dbname
    params['user'] = user
    params['host'] = 'localhost' if host is None else host
        
    if password is not None:
        params['password'] = password
         
    if port is not None:
        params['port'] = port
                
    return ' '.join(('%s=%s' % (k, v) for (k, v) in params.iteritems()))

#############################################################

INFIELDS = list(FILE_TYPES['Contributions'])
PROCFIELDS = INFIELDS + ['DCID','salted']

logging.basicConfig(level=logging.DEBUG)

def parse_date(date):
    try:
        return datetime.date(*(int(d) for d in date.split('-')))
    except ValueError:
        pass

def load_bundle_dates():
    lookup = { }
    logging.info('loading bundle dates')
    infile = open('data/tmp/nimsp_bundledates.csv')
    for record in csv.reader(infile):
        lookup[record[0]] = [parse_date(d) for d in record[1:]]
    infile.close()
    return lookup

def load_bundle_states():
    lookup = { }
    logging.info('loading bundle recipient states')
    infile = open('data/tmp/nimsp_recipientstate.csv')
    for record in csv.reader(infile):
        lookup[record[0]] = record[1]
    infile.close()
    return lookup

# new ID filter

class DCIDFilter(Filter):
    def __init__(self, id_field):
        super(DCIDFilter, self).__init__()
        self._id_field = id_field
    def process_record(self, record):
        record['DCID'] = record[self._id_field]
        record['salted'] = False
        return record

class FloatFilter(FieldFilter):
    def process_field(self, item):
        try:
            return float(item)
        except ValueError:
            pass
            
class IntFilter(FieldFilter):
    def process_field(self, item):
        try:
            return int(item)
        except ValueError:
            pass

#
# big old salt filter
#

def ensure(value, min_value, max_value):
    if value < min_value:
        return min_value
    elif value > max_value:
        return max_value
    return value

class SaltFilter(YieldFilter):
    
    def __init__(self, rando):
        super(SaltFilter, self).__init__()
        self.con = psycopg2.connect(connection_string(dbname='nimsp', host='192.168.1.70', user='data_commons', password='vitamind'))
        self.con.set_client_encoding('UTF8')
        self.cur = self.con.cursor(cursor_factory=extras.RealDictCursor)
        self.cur.execute("""UPDATE salts SET contributionid = NULL, saltid = NULL""") ################################
        self._rando = rando
    
    def get_salt(self,record):
        """
            Return an existing salt from the database, if it exists
        """
        stmt = """SELECT saltid AS contributionid, amount, date, contributor, city, state, zipcode, catcode, recipientreportsbundleid FROM salts WHERE contributionid = %s"""
        if 'ContributionID' in record:
            self.cur.execute(stmt, (record['ContributionID'],))
            return self.cur.fetchone()
        else:
            error(record,"No contributionid making salt")
            error(record,record)
            return None

    def make_salt(self, record):
        
        """
            Return a new salt entry, based on the passed record
        """
        
        salt = record.copy()
        salt['DCID'] = record['ContributionID']
        
        state = BUNDLE_STATES.get(record['RecipientReportsBundleID'], None)
        #state = record.get('State', None)
        #order_by = "state = '%s'" % state if state else "id"
        #stmt = """SELECT id, contributor, city, state, zipcode FROM salts WHERE contributionid IS NULL ORDER BY %s LIMIT 1""" % order_by
                
        stmt = """SELECT id, contributor, city, state, zipcode FROM salts WHERE contributionid IS NULL AND state = '%s' LIMIT 1""" % state
        
        self.cur.execute(stmt)
        row = self.cur.fetchone()
        #salt['State'] = state ######################## faking state... make this work
        
        if row:
        
            salt['ContributionID'] = 0 - record['ContributionID']
            salt['Contributor'] = row['contributor']
            salt['City'] = row['city']
            salt['State'] = row['state']
            salt['ZipCode'] = row['zipcode']
            salt['Occupation'] = None
            salt['NewContributor'] = None
            salt['First'] = None
            salt['Last'] = None
        
            # calculate amount alloted to the new salt
            portion = round(ensure(record['Amount'] / 100.00, 10.00, 500.00))
            record['Amount'] -= portion
            salt['Amount'] = portion
        
            # generate random date
            dates = BUNDLE_DATES.get(record['RecipientReportsBundleID'], None)
            if dates is None or dates[1] is None:
                salt['Date'] = None
            else:
                if dates[0] is None:
                    diffdays = random.randint(0, 10)
                else:
                    diff = dates[1] - dates[0]
                    diffdays = random.randint(0, diff.days)
                saltdate = dates[1] - datetime.timedelta(diffdays)
                salt['Date'] = saltdate
            
            #assign catcode
            salt['CatCode'] = 'Y0000' #uncoded

            stmt = """UPDATE salts SET contributionid = %s, saltid = %s, amount =  %s, date = %s, catcode = %s, recipientreportsbundleid = %s WHERE id = %s"""
            self.cur.execute(stmt, (record['ContributionID'], salt['ContributionID'], portion, salt['Date'], salt['CatCode'], record['RecipientReportsBundleID'], row['id']))
            self.con.commit()
        
            return salt
    
    def process_record(self, record):
        if record['Amount'] > 500.0 and random.randint(0, self._rando) == 0 and record['State']:
            record['salted'] = True
            salt = self.make_salt(record)
            if salt:
                yield salt
        yield record

# custom emitters

class AllocatedEmitter(CSVEmitter):
    def emit_record(self, record):
        if record['CatCode'] and not record['CatCode'].startswith('Z2'):
            super(AllocatedEmitter, self).emit_record(record)

class UnallocatedEmitter(CSVEmitter):
    def emit_record(self, record):
        if record['CatCode'] and record['CatCode'].startswith('Z2'):
            super(UnallocatedEmitter, self).emit_record(record)

class SaltedEmitter(CSVEmitter):
    def emit_record(self, record):
        if record['salted']:
            super(SaltedEmitter, self).emit_record(record)

class UnsaltedEmitter(CSVEmitter):
    def emit_record(self, record):
        if not record['salted']:
            super(UnsaltedEmitter, self).emit_record(record)

#
# recipe to split allocated and unallocated
#

starttime = datetime.datetime.utcnow()

# logging.info('splitting allocated and unallocated')
# 
# saucebrush.run_recipe(
#     CSVSource(open('data/tmp/nimsp_contributions.csv'), fieldnames=INFIELDS),
#     IntFilter('ContributionID'),
#     FloatFilter('Amount'),
#     DCIDFilter('ContributionID'),
#     CountEmitter(every=1000000),
#     AllocatedEmitter(open('data/tmp/nimsp_allocated_contributions.csv', 'w'), fieldnames=PROCFIELDS),
#     UnallocatedEmitter(open('data/tmp/nimsp_unallocated_contributions.csv', 'w'), fieldnames=PROCFIELDS),
# )

#
# recipe to salt and split modified/unmodified
#

BUNDLE_DATES = load_bundle_dates()
BUNDLE_STATES = load_bundle_states()

logging.info('salting unallocated contributions')

def munge_date(d):
    if d is None:
        return '0000-00-00'
    elif hasattr(d, 'isoformat'):
        return d.isoformat()
    return d

saucebrush.run_recipe(
    CSVSource(open('data/tmp/nimsp_unallocated_contributions.csv'), fieldnames=PROCFIELDS),
    IntFilter('ContributionID'),
    FloatFilter('Amount'),
    FieldModifier('salted', lambda item: item == 'True'),
    CountEmitter(every=1000000),
    SaltFilter(rando=100),
    FieldModifier('Date', munge_date),
    SaltedEmitter(open('data/tmp/nimsp_unallocated_contributions_salted.csv', 'w'), fieldnames=PROCFIELDS),
    UnsaltedEmitter(open('data/tmp/nimsp_unallocated_contributions_unsalted.csv', 'w'), fieldnames=PROCFIELDS),
)

runtime = datetime.datetime.utcnow() - starttime

print "%s seconds" % runtime.seconds