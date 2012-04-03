
import urllib
import os

from django.db import connection

from dcdata.utils.log import set_up_logger

DOWNLOAD_URL = 'http://www.fec.gov/data/IndependentExpenditure.do?format=csv&election_yr=2012' 
LOCAL_FILE = 'indexp.csv'
TABLE_NAME = 'fec_indexp_import'
SQL_POSTLOAD_FILE = os.path.join(os.path.dirname(__file__), 'postload.sql')


def reload_indexp(working_dir):
    def execute_file(filename):
        contents = " ".join([line for line in open(filename, 'r') if line[0:2] != '--'])
        statements = contents.split(';')[:-1] # split on semi-colon. Last element will be trailing whitespace

        for statement in statements:
            log.info("Executing %s" % statement)
            c.execute(statement)

    try:
        working_dir = os.path.expanduser(working_dir)
        if not os.path.isdir(working_dir):
            os.makedirs(working_dir)

        log = set_up_logger('indexp_importer', working_dir, 'IndExp Importer Fail')
        
        log.info("downloading %s to %s..." % (DOWNLOAD_URL, LOCAL_FILE))
        urllib.urlretrieve(DOWNLOAD_URL, LOCAL_FILE)
    
        log.info("uploading to table %s..." % TABLE_NAME)
        c = connection.cursor()
        c.execute("DELETE FROM %s" % TABLE_NAME)
        c.copy_expert("COPY %s FROM STDIN CSV HEADER" % TABLE_NAME, open(LOCAL_FILE, 'r'))
        execute_file(SQL_POSTLOAD_FILE)
        
        log.info("Import Succeeded.")
    except Exception as e:
        log.error(e)
        raise
    
