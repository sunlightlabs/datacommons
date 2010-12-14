import os

from dcdata.management.base.nimsp_importer import BaseNimspImporter


class NimspExtractor(BaseNimspImporter):

    IN_DIR       = '/home/datacommons/data/auto/nimsp/download/IN'
    DONE_DIR     = '/home/datacommons/data/auto/nimsp/download/DONE'
    REJECTED_DIR = '/home/datacommons/data/auto/nimsp/download/REJECTED'
    OUT_DIR      = '/home/datacommons/data/auto/nimsp/raw/IN'
    FILE_PATTERN = 'Sunlight.*.tar.gz'

    LOG_PATH = '/home/datacommons/data/auto/log/nimsp_extractor.log'

    def do_for_file(self, file, file_path):
        try:
            self.log.info('Extracting to {0}'.format(self.OUT_DIR))
            os.system('tar -C {0} -xzf {1}'.format(self.OUT_DIR, file_path))
            self.log.info('Archiving.')
            self.archive_file(file)
        except:
            self.log.warning('Something went wrong with the file extraction or archival. Rejecting {0}'.format(file))
            self.reject_file(file)


    def dry_run_for_file(self, file, file_path):
        self.log.info('Would extract {0} to {1} and then archive.'.format(file, self.OUT_DIR))


Command = NimspExtractor

