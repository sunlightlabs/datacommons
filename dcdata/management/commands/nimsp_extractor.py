from dcdata.management.base.extractor import Extractor


class NimspExtractor(Extractor):

    IN_DIR       = '/home/datacommons/data/auto/lobbying/download/IN'
    DONE_DIR     = '/home/datacommons/data/auto/lobbying/download/DONE'
    REJECTED_DIR = '/home/datacommons/data/auto/lobbying/download/REJECTED'
    OUT_DIR      = '/home/datacommons/data/auto/lobbying/raw/IN'

    FILE_PATTERN = 'Sunlight.*.tar.gz'

    LOG_PATH = '/home/datacommons/data/auto/log/nimsp_extractor.log'

    def __init__(self):
        super(NimspExtractor, self).__init__()


    def do_for_file(self, file_path):
        try:
            self.log.info('Extracting to {0}'.format(self.OUT_DIR))
            # this command needs to remove the top-level date subdirectory that NIMSP added to the archive
            os.system('tar -C {0} -xzf {1} --transform=\'s,^20[0-9][0-9]-[0-1][0-9]-[0-3][0-9]/,,\''.format(self.OUT_DIR, file_path))
            self.log.info('Archiving.')
            self.archive_file(file_path)
        except:
            self.log.warning('Something went wrong with the file extraction or archival. Rejecting {0}'.format(os.path.basename(file_path)))
            self.reject_file(file_path)


    def dry_run_for_file(self, file_path):
        self.log.info('Would extract {0} to {1} and then archive.'.format(os.path.basename(file_path), self.OUT_DIR))


Command = NimspExtractor

