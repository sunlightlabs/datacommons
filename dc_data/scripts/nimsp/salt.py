import random
import sys

import MySQLdb
import psycopg2
from psycopg2.extras import RealDictCursor

from saucebrush.filters import Filter, YieldFilter

#from nimsp_hash import pseudorandom_sample

import hashlib

def ensure(value, min_value, max_value):
    if value < min_value:
        return min_value
    elif value > max_value:
        return max_value
    return value

class DCIDFilter(Filter):
    """ Convert a nismp contribution id into our hashed transaction_id form """

    SALT = "sunlight rocks"

    def hash(self,id):
        return hashlib.md5(str(id) + self.SALT).hexdigest()

    def process_record(self, record):
        if 'contributionid' in record and record['contributionid'] is not None:
            record['transaction_id'] = self.hash(record['contributionid'])
            del(record['contributionid'])
        return record

class SaltFilter(YieldFilter):    
    def __init__(self, rando, pcon, mcon):
        super(SaltFilter, self).__init__()
        self._pcon = pcon
        self._mcon = mcon
        self._pcon.set_client_encoding('UTF8')
        self._pcur = self._pcon.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            self._mcur = self._mcon.cursor()
        except MySQLdb.Error, e:
            print "Error %d: %s" % (e.args[0], e.args[1])
            sys.exit (1)
        self._rando = rando
    
    def get_salt(self,record):
        """
            Return an existing salt from the database, if it exists
        """
        stmt = """SELECT saltid AS contributionid, amount, date as datestamp, contributor as contributor_name, city as contributor_city, state as contributor_state, zipcode as contributor_zipcode, catcode as contributor_category FROM salts WHERE contributionid = %s"""
        if 'contributionid' in record:
            self._pcur.execute(stmt, (record['contributionid'],))
            rtn = self._pcur.fetchone()
            if rtn is not None:
                rtn['amount'] = float(rtn['amount'])
                if rtn['datestamp']:
                    rtn['datestamp'] = str(rtn['datestamp'])
                    return rtn
        else:
            error(record,"No contributionid making salt")
            error(record,record)
            return None
        return None

    def make_salt(self, record):        
        """
            Return a new salt entry, based on the passed record
        """
                
        order_by = "state = '%s'" % record['contributor_state'] if record['contributor_state'] else "id"
        stmt = """SELECT id, contributor as contributor_name, city as contributor_city, state as contributor_state, zipcode as contributor_zipcode FROM salts WHERE contributionid IS NULL ORDER BY %s LIMIT 1""" % order_by
        self._pcur.execute(stmt)
        row = self._pcur.fetchone()
        if row:  
            salt = record.copy()    
            for f in ['contributor_name','contributor_city', 'contributor_state', 'contributor_zipcode']:
                salt[f] = row[f]
                salt['contributionid'] = 0 - record['contributionid']
        
            # calculate amount alloted to the new salt
            portion = ensure(round(record['amount'] / 100.00), 10.00, 500.00)
            record['amount'] -= portion
            salt['amount'] = portion
                
            #get date from an average for this report bundle of contributions
            if record['datestamp'] and record['datestamp'] != "":
                salt['datestamp'] = record['datestamp']
            else:
                salt['datestamp'] = None
            stmt = """SELECT date(from_unixtime(AVG(unix_timestamp(date)))) AS datestamp FROM Contributions WHERE date IS NOT NULL AND RecipientReportsBundleID = (SELECT RecipientReportsBundleID FROM Contributions WHERE ContributionID = %s)""";
            try:
                self._mcur.execute(stmt, (record['contributionid'],))
                d = (self._mcur.fetchone())[0]
                if d and d != '1969-12-31':
                    salt['datestamp'] = d
            except Exception, e:
                print e
                sys.exit()
            
            #assign catcode
            salt['contributor_category'] = 'Y0000' #uncoded

            stmt = """UPDATE salts SET contributionid = %s, saltid = %s, amount = %s, catcode = %s WHERE id = %s"""
            self._pcur.execute(stmt, (record['contributionid'], salt['contributionid'], salt['amount'], salt['contributor_category'], row['id']))
            self._pcon.commit()

            salt['salted'] = True
            return salt
        else:
            return None
    
    def process_record(self, record):
        record['salted'] = False
        if record['amount'] > 500.0:
            salt = self.get_salt(record)
            if salt is not None:
                record['amount'] -= salt['amount']
                record['salted'] = True
                yield salt
            elif random.randint(0, self._rando) == 0:
            #elif pseudorandom_sample(record['contributionid'], self._rando):
                salt = self.make_salt(record)
                if salt is not None:
                    record['salted'] = True
                    yield salt
        yield record
