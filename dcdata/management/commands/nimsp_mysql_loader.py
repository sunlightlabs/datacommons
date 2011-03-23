import os

from dcdata.management.base.nimsp_importer import BaseNimspImporter


class NimspMysqlLoader(BaseNimspImporter):

    IN_DIR       = '/home/datacommons/data/auto/nimsp/raw/IN'
    DONE_DIR     = '/home/datacommons/data/auto/nimsp/raw/DONE'
    REJECTED_DIR = '/home/datacommons/data/auto/nimsp/raw/REJECTED'
    OUT_DIR      = '/home/datacommons/data/auto/nimsp/dump/IN'
    FILE_PATTERN = '*.sql'

    LOG_PATH = '/home/datacommons/data/auto/log/nimsp_mysql_loader.log'


    def do_for_file(self, file, file_path):
        try:
            self.log.info('Importing {0}'.format(file))
            os.system('mysql nimsp --execute=\'source {0}\''.format(file_path))
            self.log.info('Archiving.')
            self.archive_file(file, timestamp=True)

            outfile_path = os.path.join(self.OUT_DIR, 'do_dump.txt')
            os.system('touch {0}'.format(outfile_path))
        except:
            self.log.warning('Something went wrong with the MySQL import or archive. Rejecting {0}'.format(file))
            self.reject_file(file)


    def dry_run_for_file(self, file, file_path):
        self.log.info('Would import {0} and archive'.format(file))



Command = NimspMysqlLoader

