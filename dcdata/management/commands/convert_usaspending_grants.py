from dcdata.management.base.usaspending_importer import BaseUSASpendingConverter
from dcdata.grants.models import Grant
from dcdata.scripts.usaspending import faads


class Command(BaseUSASpendingConverter):
    FILE_PATTERN = '*_All_[!Contracts]_Full_*.csv' # Basically, any file without Contracts

    modelclass = Grant
    outfile_basename = 'grants'
    module = faads


    def __init__(self):
        super(Command, self).__init__()


