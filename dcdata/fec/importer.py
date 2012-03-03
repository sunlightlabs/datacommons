import os
import subprocess
import tempfile
import urllib
import us.fec

from collections import namedtuple
from dcdata.utils.log import set_up_logger
from django.db import connection


F = namedtuple('F', ['url', 'dta_file', 'schema_file', 'sql_table'])

# note: tables will be created/destroyed in this order. So must do dependant tables first to avoid constraint errors.
FEC_CONFIG = [
    F('ftp://ftp.fec.gov/FEC/indiv12.zip', 'itcont.dta', 'fec_individual_contributions.csv', 'fec_indiv_import'),
    F('ftp://ftp.fec.gov/FEC/pas212.zip', 'itpas2.dta', 'fec_contributions_to_candidates.csv', 'fec_pac2cand_import'),
    F('ftp://ftp.fec.gov/FEC/oth12.zip', 'itoth.dta', 'fec_committee_transactions.csv', 'fec_pac2pac_import'),
    F('ftp://ftp.fec.gov/FEC/cm12.zip', 'foiacm.dta', 'fec_committee_master_schema.csv', 'fec_committees'),
    F('ftp://ftp.fec.gov/FEC/cn12.zip', 'foiacn.dta', 'fec_candidate_master_schema.csv', 'fec_candidates_import'),
    F('ftp://ftp.fec.gov/FEC/webl12.zip', 'FECWEB/webl12.dat', 'fec_candidate_summary.csv', 'fec_candidate_summaries_import'),
]

# for loading PAC summaries. Used for SuperDonors project, but not currently used in Brisket.
FEC_PAC_SUMMARY_CONFIG = [
    F('ftp://ftp.fec.gov/FEC/webk%s.zip' % year, 'FECWEB/webk%s.dat' % year, 'fec_pac_summary.csv', 'fec_pac_summaries_%s' % year)
    for year in '00 02 04 06 08 10'.split()
] + [
    F('ftp://ftp.fec.gov/FEC/1992/pacsum92.zip', 'NP921.TAP', 'pacsum.csv', 'fec_early_pac_summaries_%s' % year[2:4]),
    F('ftp://ftp.fec.gov/FEC/1994/pacsum94.zip', 'PACSUM94.DAT', 'pacsum.csv', 'fec_early_pac_summaries_%s' % year[2:4]),
    F('ftp://ftp.fec.gov/FEC/1996/pacsum96.zip', 'PACSUM96.DAT', 'pacsum.csv', 'fec_early_pac_summaries_%s' % year[2:4]),
    F('ftp://ftp.fec.gov/FEC/1998/pacsum98.zip', 'R98/RDATA/NPTAP1.TAP', 'pacsum.csv', 'fec_early_pac_summaries_%s' % year[2:4]),
    F('ftp://ftp.fec.gov/FEC/2000/pacsum00.zip', 'pacsum%s.txt', 'pacsum.csv', 'fec_early_pac_summaries_%s' % year[2:4]),
    F('ftp://ftp.fec.gov/FEC/2002/pacsum02.zip', 'pacsum%s.txt', 'pacsum.csv', 'fec_early_pac_summaries_%s' % year[2:4]),
    F('ftp://ftp.fec.gov/FEC/2004/pacsum04.zip', 'pacsum%s.txt', 'pacsum.csv', 'fec_early_pac_summaries_%s' % year[2:4]),
]

SCHEMA_ROOT = os.path.dirname(us.fec.__file__)

SQL_PRELOAD_FILE = os.path.join(os.path.dirname(__file__), 'preload.sql')
SQL_POSTLOAD_FILE = os.path.join(os.path.dirname(__file__), 'postload.sql')


class FECImporter():
    def __init__(self, processing_dir=None):
        if not processing_dir:
            processing_dir = tempfile.mkdtemp(prefix='tmp_fec_')

        self.processing_dir = processing_dir

        self.log = set_up_logger('fec_importer', self.processing_dir, 'Unhappy FEC Importer')

        print "Processing files in {0}".format(self.processing_dir)
        self.log.info("Processing files in {0}".format(self.processing_dir))

        self.update_csv()
        self.update_db()


    def update_csv(self):

        self.log.info("Downloading files to %s..." % self.processing_dir)
        self.download()

        self.log.info("Extracting files...")
        self.extract()

        self.log.info("Converting to unicode...")
        self.fix_unicode()

        self.log.info("Converting to CSV...")
        self.fec_2_csv()


    def update_db(self):

        c = connection.cursor()

        self.execute_file(c, SQL_PRELOAD_FILE)

        self.log.info("Uploading data...")
        self.upload(c)

        self.log.info("Processing uploaded data...")
        self.execute_file(c, SQL_POSTLOAD_FILE)

        self.log.info("Done.")


    def download(self):
        if not os.path.isdir(self.processing_dir):
            os.makedirs(self.processing_dir)

        for conf in FEC_CONFIG:
            local_file = os.path.join(self.processing_dir, conf.url.split("/")[-1])
            self.log.info("downloading %s to %s..." % (conf.url, local_file))
            urllib.urlretrieve(conf.url, local_file)


    def extract(self):
        abs_source = os.path.expanduser(self.processing_dir)
        subprocess.check_call(['unzip', '-oqu', os.path.join(abs_source, "*.zip"), "-d" + abs_source])


    def fix_unicode(self):
        abs_source = os.path.expanduser(self.processing_dir)
        for conf in FEC_CONFIG:
            infile = open(os.path.join(abs_source, conf.dta_file), 'r')
            outfile = open(os.path.join(abs_source, conf.dta_file + ".utf8"), 'w')

            for line in infile:
                fixed_line = line.decode('utf8', 'replace').encode('utf8', 'replace')
                outfile.write(fixed_line)


    def fec_2_csv(self):
        abs_source = os.path.expanduser(self.processing_dir)
        for conf in FEC_CONFIG:
            outfile = open(os.path.join(abs_source, conf.dta_file.split(".")[0] + ".csv"), 'w')
            subprocess.check_call(
                ['sort -u %s | in2csv -f fixed --schema=%s' % (os.path.join(abs_source, conf.dta_file + ".utf8"), os.path.join(SCHEMA_ROOT, conf.schema_file))],
                shell=True, stdout=outfile)


    def execute_file(self, cursor, filename):
        contents = " ".join([line for line in open(filename, 'r') if line[0:2] != '--'])
        statements = contents.split(';')[:-1] # split on semi-colon. Last element will be trailing whitespace

        for statement in statements:
            self.log.info("Executing %s" % statement)
            cursor.execute(statement)


    def upload(self, c):
        abs_source = os.path.expanduser(self.processing_dir)

        for conf in FEC_CONFIG:
            infile = open(os.path.join(abs_source, conf.dta_file.split(".")[0] + ".csv"), 'r')
            c.execute("DELETE FROM %s" % conf.sql_table)
            c.copy_expert("COPY %s FROM STDIN CSV HEADER" % conf.sql_table, infile)


