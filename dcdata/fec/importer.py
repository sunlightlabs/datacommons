import os
import subprocess
import urllib

from collections import namedtuple
from dcdata.utils.log import set_up_logger
from django.db import connection, transaction
from django.core.management import call_command


F = namedtuple('F', ['url', 'filename', 'sql_table'])

SQL_PRELOAD_FILE = os.path.join(os.path.dirname(__file__), 'preload.sql')
SQL_POSTLOAD_FILE = os.path.join(os.path.dirname(__file__), 'postload.sql')
CYCLES = range(1996, 2014, 2)


class FECImporter():

    def __init__(self, processing_dir, cycle, skip_download=False):
        self.processing_dir = os.path.expanduser(processing_dir)
        self.configs_by_cycle = self._get_configs_by_cycle()
        self.cycle = cycle
        self.cycle_config = self.configs_by_cycle[str(self.cycle)]
        self.skip_download = skip_download

        self.log = set_up_logger('fec_importer', self.processing_dir, 'Unhappy FEC Importer')

    @transaction.commit_manually()
    def run(self):
        if not self.skip_download:
            try:
                self.log.info("Downloading files to %s..." % self.processing_dir)
                self.download()

                self.log.info("Extracting files...")
                self.extract()

                self.log.info("Converting to unicode...")
                self.fix_unicode()

            except Exception as e:
                self.log.error(e)
                raise

        # TODO: move this back
        self.log.info("Removing any duplicates from candidates/committees file...")
        self.dedupe_file()


        try:
            c = connection.cursor()

            self.log.info("Creating temporary tables...")
            self._create_temp_tables(c)

            self.log.info("Loading data into temp tables...")
            self.load(c)

            self.log.info("Restoring columns which were not in CSV and manually populating cycle on tables which require it...")
            self.restore_calculated_fields(c)

            #self.log.info("Finding what cycles are in this set of files...")
            #self.get_cycles_from_data(c)

            self.log.info("Dropping and recreating partitions for this cycle ({})...".format(self.cycle))
            self.recreate_partitions()

            self.log.info("Inserting out of date cycle records.")
            self.insert_out_of_date_cycle_records(c)

            self.log.info("Processing loaded data...")
            self.execute_file(c, SQL_POSTLOAD_FILE)

            self.log.info("Deleting out of date cycle records.")
            self.delete_out_of_date_cycle_records(c)

            self.log.info("Committing.")
            transaction.commit()

            self.log.info("Done.")
        except Exception as e:
            transaction.rollback()

            self.log.exception(e)
            raise

    def insert_out_of_date_cycle_records(self, cursor):
        cursor.execute('insert into fec_out_of_date_cycles (cycle) values (%s)' % self.cycle)
        self._log_rows_affected(cursor)

    def delete_out_of_date_cycle_records(self, cursor):
        cursor.execute('delete from fec_out_of_date_cycles where cycle = %s' % self.cycle)
        self._log_rows_affected(cursor)

    def _create_temp_tables(self, c):
        self.execute_file(c, SQL_PRELOAD_FILE)

    def restore_calculated_fields(self, cursor):
        """
        Certain tables have calculated fields that didn't exist in the original CSV,
        so we removed them from the temp tables. Now that the import is over, we add
        them back and populate them with values if necessary.
        
        (Most tables have a date that can be converted to a cycle, but not all.)
        """

        # We need to add the column back on. It was previously removed (relative to the permanent table),
        # so that we didn't have to alter our COPY commands (since cycle isn't in the file).
        cursor.execute('alter table %s add column race varchar(7)' % self.temp_table_name('fec_candidates'))

        for table in 'fec_candidates fec_committees fec_candidate_summaries fec_committee_summaries fec_indiv fec_pac2cand fec_pac2pac'.split():
            cursor.execute('alter table %s add column cycle smallint' % self.temp_table_name(table))

        for table in 'fec_candidates fec_committees fec_candidate_summaries fec_committee_summaries'.split():
            cursor.execute('update %s set cycle = %s' % (self.temp_table_name(table), self.cycle))

        for table in 'fec_indiv fec_pac2cand fec_pac2pac'.split():
            cursor.execute("""
                update {} set cycle = case when "date" is null then {} else to_cycle(to_date("date", 'MMDDYYYY')) end
            """.format(self.temp_table_name(table), self.cycle))

    def load(self, c):
        for conf in self.cycle_config:
            infile = open(self._working_filename(conf) + '.utf8', 'r')
            tmp_table = 'tmp_{}'.format(conf.sql_table)
            # note: quote character is an arbitrary ASCII code that is unlikely to appear in data.
            # FEC uses single and double quotes and most other printable characters in the data,
            # so we have to be sure not to misinterpret any of them as semantically meaningful.
            c.copy_expert("COPY %s FROM STDIN CSV HEADER DELIMITER '|' QUOTE E'\\x01'" % tmp_table, infile)

    def _download_file(self, conf):
        filename = conf.url.split("/")[-1]
        dirname = filename.split(".")[0]
        return os.path.join(self.processing_dir, dirname, filename)

    def execute_file(self, cursor, filename):
        contents = " ".join([line for line in open(filename, 'r') if line[0:2] != '--'])
        statements = contents.split(';')[:-1]  # split on semi-colon. Last element will be trailing whitespace

        for statement in statements:
            self.log.info("Executing %s" % statement)
            cursor.execute(statement)
            self._log_rows_affected(cursor)

    def _working_dir(self, conf):
        filename = conf.url.split("/")[-1]
        dirname = filename.split(".")[0]
        return os.path.join(self.processing_dir, dirname)

    def download(self):
        for conf in self.cycle_config:
            if not os.path.isdir(self._working_dir(conf)):
                os.makedirs(self._working_dir(conf))

            self.log.info("Downloading %s to %s..." % (conf.url, self._download_file(conf)))
            urllib.urlretrieve(conf.url, self._download_file(conf))

    def extract(self):
        for conf in self.cycle_config:
            subprocess.check_call(['unzip', '-oqu', self._download_file(conf), "-d" + self._working_dir(conf)])

    def fix_unicode(self):
        for conf in self.cycle_config:
            filename = self._working_filename(conf)
            infile = open(filename, 'r')
            outfile = open(filename + ".utf8", 'w')

            for line in infile:
                fixed_line = line.decode('utf8', 'replace').encode('utf8', 'replace').replace('\x01', '')
                outfile.write(fixed_line)

    def dedupe_file(self):
        for conf in self.cycle_config:
            if conf.sql_table in 'fec_candidates fec_committees'.split():
                filename = self._working_filename(conf) + '.utf8'
                subprocess.check_call(['cp {0} {0}.tmp'.format(filename)], shell=True)
                subprocess.check_call(['uniq {0}.tmp > {0}'.format(filename)], shell=True)
                subprocess.check_call(['rm {}.tmp'.format(filename)], shell=True)

    def _working_filename(self, config):
        return os.path.join(self._working_dir(config), config.filename)

    # This is not needed, but not getting rid of it just yet.
    #def get_cycles_from_data(self, c):
    #    """
    #    The files contain data for cycles which are out of bounds for the file.
    #    Query the temporary load tables to find out what cycles we're working with.
    #    """

    #    table_cycles = {}
    #    for conf in self.cycle_config:
    #        self.log.info(table_cycles)
    #        c.execute('select distinct cycle from {}'.format(self.temp_table_name(conf.sql_table)))
    #        table_cycles[self.temp_table_name(conf.sql_table)] = c.fetchall()

    #    self.log.info(table_cycles)

    def recreate_partitions(self):
        for conf in self.cycle_config:
            call_command('delete_partition__fec', table=conf.sql_table, cycle=self.cycle)
            call_command('create_partition__fec', table=conf.sql_table, cycle=self.cycle)

    def temp_table_name(self, table):
        return 'tmp_{}'.format(table)

    def _get_configs_by_cycle(self):
        return {str(c): self._get_config_for_cycle(str(c)) for c in CYCLES}

    def _get_config_for_cycle(self, cycle):
        if len(cycle) == 4:
            cycle4 = cycle
            cycle2 = cycle[2:]
        elif len(cycle) == 2:
            cycle2 = cycle
            cycle4 = '20%s' % cycle if int(cycle) < 50 else '19%s' % cycle
        else:
            raise Exception("Unknown cycle %s" % cycle)

        """
        Note: Tables will be created/destroyed in this order.
        So, must do dependant tables first to avoid constraint errors.
        """
        return [
            F('ftp://ftp.fec.gov/FEC/%s/indiv%s.zip' % (cycle4, cycle2), 'itcont.txt', 'fec_indiv'),
            F('ftp://ftp.fec.gov/FEC/%s/pas2%s.zip' % (cycle4, cycle2), 'itpas2.txt', 'fec_pac2cand'),
            F('ftp://ftp.fec.gov/FEC/%s/oth%s.zip' % (cycle4, cycle2), 'itoth.txt', 'fec_pac2pac'),
            F('ftp://ftp.fec.gov/FEC/%s/cm%s.zip' % (cycle4, cycle2), 'cm.txt', 'fec_committees'),
            F('ftp://ftp.fec.gov/FEC/%s/cn%s.zip' % (cycle4, cycle2), 'cn.txt', 'fec_candidates'),
            F('ftp://ftp.fec.gov/FEC/%s/weball%s.zip' % (cycle4, cycle2), 'weball%s.txt' % cycle2, 'fec_candidate_summaries'),
            F('ftp://ftp.fec.gov/FEC/%s/webk%s.zip' % (cycle4, cycle2), 'webk%s.txt' % cycle2, 'fec_committee_summaries')
        ]

    def _log_rows_affected(self, cursor):
        self.log.debug('Rows affected: {}'.format(cursor.rowcount))
