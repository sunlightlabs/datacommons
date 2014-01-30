
import urllib
import os

from django.db import connection

from dcdata.utils.log import set_up_logger

# Note that while the query param says "election year," the files for off-years do seem
# to be empty, so we'll assume two-year cycles work for now.
DOWNLOAD_URL = 'http://www.fec.gov/data/IndependentExpenditure.do?format=csv&election_yr={}' 
LOCAL_FILE = 'indexp.csv'
TABLE_NAME = 'fec_indexp_import'
SQL_POSTLOAD_FILE = os.path.join(os.path.dirname(__file__), 'postload.sql')


def reload_indexp(working_dir, cycle):
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
        
        local_file_path = os.path.join(working_dir, LOCAL_FILE)
        log.info("downloading %s to %s..." % (DOWNLOAD_URL.format(cycle), local_file_path))
        urllib.urlretrieve(DOWNLOAD_URL.format(cycle), local_file_path)
    
        log.info("uploading to table %s..." % TABLE_NAME)
        c = connection.cursor()
        c.execute("insert into fec_indexp_out_of_date_cycles (cycle) values ({})".format(cycle))
        c.execute("DELETE FROM %s" % TABLE_NAME)
        c.copy_expert("COPY %s (candidate_id, candidate_name, spender_id, spender_name, election_type, candidate_state, candidate_district, candidate_office, candidate_party, amount, date, aggregate_amount, support_oppose, purpose, payee, filing_number, amendment, transaction_id, image_number, received_date, prev_file_num) FROM STDIN CSV HEADER NULL ' ' " % TABLE_NAME, open(local_file_path, 'r'))
        c.execute("update {} set cycle = {}".format(TABLE_NAME, cycle))
        execute_file(SQL_POSTLOAD_FILE)
        c.execute("delete from fec_indexp_out_of_date_cycles")
        
        log.info("Import Succeeded.")
    except Exception as e:
        log.error(e)
        raise
    
