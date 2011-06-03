import os

from dcdata.management.base.nimsp_importer import BaseNimspImporter


class NimspMysqlLoader(BaseNimspImporter):

    IN_DIR       = '/home/datacommons/data/auto/nimsp/raw/IN'
    DONE_DIR     = '/home/datacommons/data/auto/nimsp/raw/DONE'
    REJECTED_DIR = '/home/datacommons/data/auto/nimsp/raw/REJECTED'
    OUT_DIR      = '/home/datacommons/data/auto/nimsp/dump/IN'
    FILE_PATTERN = '*.sql'


    def do_for_file(self, file_path):
        file = os.path.basename(file_path)
        outfile_path = os.path.join(self.OUT_DIR, 'do_dump.txt')
        try:
            # avoid a race condition with the next script by deleting the trigger file
            # the ideal solution (instead) would be to have a run_when_finished() method
            # in which to touch the trigger file
            if os.path.exists(outfile_path):
                os.remove(outfile_path)

            self.log.info('Importing {0}'.format(file))
            os.system('mysql nimsp --execute=\'source {0}\''.format(file_path))
            self.log.info('Archiving.')
            self.archive_file(file, timestamp=True)

            # this file will trigger the next script in the pipeline
            os.system('touch {0}'.format(outfile_path))
        except:
            self.log.warning('Something went wrong with the MySQL import or archive. Rejecting {0}'.format(file))
            self.reject_file(file)


    def dry_run_for_file(self, file_path):
        file = os.path.basename(file_path)
        self.log.info('Would import {0} and archive'.format(file))



Command = NimspMysqlLoader

