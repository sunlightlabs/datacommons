
import urllib
import os

from django.db import connection

from dcdata.fec.importer import execute_file


DOWNLOAD_URL = 'http://www.fec.gov/data/IndependentExpenditure.do?format=csv'
LOCAL_FILE = 'indexp.csv'
TABLE_NAME = 'fec_indexp_import'
SQL_POSTLOAD_FILE = os.path.join(os.path.dirname(__file__), 'postload.sql')


def reload_indexp(working_dir):
    working_dir = os.path.expanduser(working_dir)
    if not os.path.isdir(working_dir):
        os.makedirs(working_dir)
        
    print "downloading %s to %s..." % (DOWNLOAD_URL, LOCAL_FILE)
    urllib.urlretrieve(DOWNLOAD_URL, LOCAL_FILE)
    
    print "uploading to table %s..." % TABLE_NAME
    c = connection.cursor()
    c.execute("DELETE FROM %s" % TABLE_NAME)
    c.copy_expert("COPY %s FROM STDIN CSV HEADER" % TABLE_NAME, open(LOCAL_FILE, 'r'))
    
    execute_file(c, SQL_POSTLOAD_FILE)
    
    
