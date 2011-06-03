import os

from dcdata.management.base.extractor import Extractor


class LobbyingExtractor(Extractor):

    IN_DIR       = '/home/datacommons/data/auto/lobbying/download/IN'
    DONE_DIR     = '/home/datacommons/data/auto/lobbying/download/DONE'
    REJECTED_DIR = '/home/datacommons/data/auto/lobbying/download/REJECTED'
    OUT_DIR      = '/home/datacommons/data/auto/lobbying/raw/IN'

    FILE_PATTERN = 'Lobby*.zip'

    def __init__(self):
        super(LobbyingExtractor, self).__init__()


    def extract(self, file_path):
        os.system('unzip {0} -d {1}'.format(file_path, self.OUT_DIR))


Command = LobbyingExtractor

