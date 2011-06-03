import os

from dcdata.management.base.importer import BaseImporter


class Extractor(BaseImporter):

    IN_DIR       = None # '/home/datacommons/data/auto/nimsp/download/IN'
    DONE_DIR     = None # '/home/datacommons/data/auto/nimsp/download/DONE'
    REJECTED_DIR = None # '/home/datacommons/data/auto/nimsp/download/REJECTED'
    OUT_DIR      = None # '/home/datacommons/data/auto/nimsp/raw/IN'
    FILE_PATTERN = None # 'Sunlight.*.tar.gz'


    def __init__(self):
        super(Extractor, self).__init__()
        self._check_attribute(self.IN_DIR)
        self._check_attribute(self.DONE_DIR)
        self._check_attribute(self.REJECTED_DIR)
        self._check_attribute(self.OUT_DIR)
        self._check_attribute(self.FILE_PATTERN)


    def do_for_file(self, file_path):
        try:
            self.log.info('Extracting to {0}'.format(self.OUT_DIR))
            self.extract(file_path)
            self.log.info('Archiving.')
            self.archive_file(file_path)
        except:
            self.log.warning('Something went wrong with the file extraction or archival. Rejecting {0}'.format(os.path.basename(file_path)))
            self.reject_file(file_path)


    def extract(self, file_path):
        os.system('tar -C {0} -xzf {1}'.format(self.OUT_DIR, file_path))


    def dry_run_for_file(self, file_path):
        self.log.info('Would extract {0} to {1} and then archive.'.format(os.path.basename(file_path), self.OUT_DIR))


    def _check_attribute(self, attr_name):
        if not getattr(self, attr_name):
            self.log.error("You must assign a value to {0} in the child Extractor class".format(attr_name))


Command = Extractor

