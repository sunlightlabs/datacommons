import os
import subprocess
import urllib
import us.fec

from collections import namedtuple
from dcdata.utils.log import set_up_logger
from django.db import connection


F = namedtuple('F', ['url', 'dta_file', 'schema_file', 'sql_table'])

# note: tables will be created/destroyed in this order. So must do dependant tables first to avoid constraint errors.
FEC_CONFIG = [
    F('ftp://ftp.fec.gov/FEC/2012/indiv12.zip', 'itcont.dta', None, 'fec_indiv_import'),
    F('ftp://ftp.fec.gov/FEC/2012/pas212.zip', 'itpas2.dta', None, 'fec_pac2cand_import'),
    F('ftp://ftp.fec.gov/FEC/2012/oth12.zip', 'itoth.dta', None, 'fec_pac2pac_import'),
    F('ftp://ftp.fec.gov/FEC/cm12.zip', 'foiacm.dta', 'fec_committee_master_schema.csv', 'fec_committees'),
    F('ftp://ftp.fec.gov/FEC/cn12.zip', 'foiacn.dta', 'fec_candidate_master_schema.csv', 'fec_candidates_import'),
    F('ftp://ftp.fec.gov/FEC/weball12.zip', 'FECWEB/webl12.all', 'fec_candidate_summary.csv', 'fec_candidate_summaries_import'),
    F('ftp://ftp.fec.gov/FEC/webk12.zip', 'FECWEB/webk12.dat', 'fec_pac_summary.csv', 'fec_committee_summaries_import')
]

SCHEMA_ROOT = os.path.dirname(us.fec.__file__)

SQL_PRELOAD_FILE = os.path.join(os.path.dirname(__file__), 'preload.sql')
SQL_POSTLOAD_FILE = os.path.join(os.path.dirname(__file__), 'postload.sql')
VIRTUALENV_ACTIVATE = os.path.expanduser('~datacommons/.virtualenvs/datacommons/bin/activate')


class FECImporter():
    def __init__(self, processing_dir, config=FEC_CONFIG):
        self.processing_dir = os.path.expanduser(processing_dir)
        self.FEC_CONFIG = config

        self.log = set_up_logger('fec_importer', self.processing_dir, 'Unhappy FEC Importer')


    def update_csv(self):
        try:
            self.log.info("Downloading files to %s..." % self.processing_dir)
            self.download()

            self.log.info("Extracting files...")
            self.extract()

            self.log.info("Converting to unicode...")
            self.fix_unicode()

            self.log.info("Converting to CSV...")
            self.fec_2_csv()
        except Exception as e:
            self.log.error(e)
            raise


    def update_db(self):
        try:
            c = connection.cursor()

            self.execute_file(c, SQL_PRELOAD_FILE)

            self.log.info("Uploading data...")
            self.upload(c)

            self.log.info("Processing uploaded data...")
            self.execute_file(c, SQL_POSTLOAD_FILE)

            self.log.info("Done.")
        except Exception as e:
            self.log.error(e)
            raise

    def _download_file(self, conf):
        filename = conf.url.split("/")[-1]
        dirname = filename.split(".")[0]
        return os.path.join(self.processing_dir, dirname, filename)
        
    def _working_dir(self, conf):
        filename = conf.url.split("/")[-1]
        dirname = filename.split(".")[0]
        return os.path.join(self.processing_dir, dirname)

    def download(self):
        for conf in self.FEC_CONFIG:
            if not os.path.isdir(self._working_dir(conf)):
                os.makedirs(self._working_dir(conf))

            self.log.info("downloading %s to %s..." % (conf.url, self._download_file(conf)))
            urllib.urlretrieve(conf.url, self._download_file(conf))


    def extract(self):
        for conf in self.FEC_CONFIG:
            subprocess.check_call(['unzip', '-oqu', self._download_file(conf), "-d" + self._working_dir(conf)])


    def fix_unicode(self):
        for conf in self.FEC_CONFIG:
            infile = open(os.path.join(self._working_dir(conf), conf.dta_file), 'r')
            outfile = open(os.path.join(self._working_dir(conf), conf.dta_file + ".utf8"), 'w')

            for line in infile:
                fixed_line = line.decode('utf8', 'replace').encode('utf8', 'replace')
                outfile.write(fixed_line)


    def fec_2_csv(self):
        for conf in self.FEC_CONFIG:
            infile = os.path.join(self._working_dir(conf), conf.dta_file + ".utf8")
            outfile = open(os.path.join(self._working_dir(conf), conf.dta_file.split(".")[0] + ".csv"), 'w')
            if conf.schema_file:
                subprocess.check_call(
                    ['. %s && sort -u %s | in2csv -f fixed --schema=%s -d "|"' % (VIRTUALENV_ACTIVATE, infile, os.path.join(SCHEMA_ROOT, conf.schema_file))],
                    shell=True, stdout=outfile)
            else:
                subprocess.check_call( ['sort -u %s ' % infile],
                    shell=True, stdout=outfile)

    def execute_file(self, cursor, filename):
        contents = " ".join([line for line in open(filename, 'r') if line[0:2] != '--'])
        statements = contents.split(';')[:-1] # split on semi-colon. Last element will be trailing whitespace

        for statement in statements:
            self.log.info("Executing %s" % statement)
            cursor.execute(statement)


    def upload(self, c):

        for conf in self.FEC_CONFIG:
            infile = open(os.path.join(self._working_dir(conf), conf.dta_file.split(".")[0] + ".csv"), 'r')
            c.execute("DELETE FROM %s" % conf.sql_table)
            c.copy_expert("COPY %s FROM STDIN CSV HEADER DELIMITER '%s'" % (conf.sql_table, ',' if conf.schema_file else '|'), infile)

