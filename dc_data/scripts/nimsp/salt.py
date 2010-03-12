import hashlib
import random
import sys

import sqlite3
import psycopg2
from psycopg2.extras import RealDictCursor

from saucebrush.filters import Filter, YieldFilter

def ensure(value, min_value, max_value):
    if value < min_value:
        return min_value
    elif value > max_value:
        return max_value
    return value

def sqlite_dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


class DCIDFilter(Filter):
    """ Convert a nismp contribution id into our encoded transaction_id form """
    def __init__(self, salt_key="tmp"):
        super(DCIDFilter, self).__init__()
        self._salt_key = salt_key

    def encode(self,id):
        return hashlib.md5(str(id) + self._salt_key).hexdigest()

    def process_record(self, record):
        record['transaction_id_original'] = record['contributionid']
        record['transaction_id_salt_key'] = self._salt_key
        record['transaction_id'] = self.encode(record['contributionid'])
        del(record['contributionid'])
        return record

class SaltFilter(YieldFilter):    
    def __init__(self, rando, salt_db, dcid_filter):
        super(SaltFilter, self).__init__()
        self._saltcon = sqlite3.connect(salt_db)
        self._saltcon.row_factory = sqlite_dict_factory
        self._dcid_filter = dcid_filter
        try:
            self._saltcur = self._saltcon.cursor()
        except Exception, e:
            print "Error: %s" % (e)
            sys.exit(1)
        self._rando = rando
    
    def get_salt(self,record):
        """
            Return an existing salt from the database, if it exists
        """
        
        stmt = """SELECT contributor as contributor_name, city as contributor_city, state as contributor_state,
                         zipcode as contributor_zipcode, catcode as contributor_category, amount, date
                  FROM salts WHERE nimsp_id = ?"""
        if 'contributionid' in record:
            self._saltcur.execute(stmt, (record['contributionid'],))
            row = self._saltcur.fetchone()
            if row is not None:
                salt = record.copy()
                salt['contributionid'] = 0 - record['contributionid']
                salt['contributor_name'] = row['contributor_name']
                salt['contributor_city'] = row['contributor_city']
                salt['contributor_state'] = row['contributor_state']
                salt['contributor_zipcode'] = row['contributor_zipcode']
                salt['contributor_category'] = row['contributor_category']
                salt['amount'] = float(row['amount'])
                if salt['date']:
                    salt['date'] = str(row['date'])
                salt['salted'] = True
                return salt
        else:
            print "No contributionid making salt: %s" % record

    def make_salt(self, record):        
        """
            Return a new salt entry, based on the passed record
        """
        
        stmt = """SELECT id, contributor as contributor_name, city as contributor_city,
                         state as contributor_state, zipcode as contributor_zipcode
                  FROM salts
                  WHERE nimsp_id = '' AND contributor_state = ?
                  LIMIT 1"""
        self._saltcur.execute(stmt, (record.get('contributor_state', ''),))
        row = self._saltcur.fetchone()
        
        if not row:
            #raise ValueError('no more unused salt entries in the database')
            return
        
        salt = record.copy()    
        for f in ['contributor_name','contributor_city', 'contributor_state', 'contributor_zipcode']:
            salt[f] = row[f]
        salt['contributionid'] = 0 - record['contributionid']
    
        # calculate amount alloted to the new salt
        portion = ensure(round(record['amount'] / 100.00), 10.00, 500.00)
        record['amount'] -= portion
        salt['amount'] = portion
            
        #get date from an average for this report bundle of contributions
        if record['date'] and record['date'] != "":
            salt['date'] = record['date']
        else:
            salt['date'] = None
        stmt = """SELECT date(from_unixtime(AVG(unix_timestamp(date)))) FROM Contributions WHERE date IS NOT NULL AND RecipientReportsBundleID = (SELECT RecipientReportsBundleID FROM Contributions WHERE ContributionID = %s)""";
        try:
            self._mcur.execute(stmt, (record['contributionid'],))
            d = (self._mcur.fetchone())[0]
            if d and (str(d) != '1969-12-31'):
                salt['date'] = d
        except Exception, e:
            print e
            sys.exit(1)
        
        #assign catcode
        salt['contributor_category'] = 'Y0000' #uncoded

        record_hash = self._dcid_filter.encode(record['contributionid'])
        salt_hash = self._dcid_filter.encode(salt['contributionid'])

        stmt = """UPDATE salts SET nimsp_id = ?, salt_key = ?, record_hash = ?, salt_hash = ?, amount = ?, date = ?, catcode = ? WHERE id = ?"""
        self._saltcur.execute(stmt, (record['contributionid'], self._dcid_filter._salt_key, record_hash, salt_hash, salt['amount'],  salt['date'], salt['contributor_category'], row['id']))
        self._saltcon.commit()
        
        salt['salted'] = True
        
        return salt
    
    def process_record(self, record):
        record['salted'] = False
        salt = self.get_salt(record)
        if salt is not None:
            record['amount'] -= salt['amount']
            record['salted'] = True
            yield salt
        elif record['amount'] > 500.0:
            if random.randint(0, self._rando) == 0:
                salt = self.make_salt(record)
                if salt is not None:
                    record['salted'] = True
                    yield salt
                else:
                    print "Didn't make salt: %s" % record
        yield record
