from dcdata.management.base.usaspending_importer import BaseUSASpendingConverter
from dcdata.grants.models import Grant
from dcdata.scripts.usaspending import faads


class Command(BaseUSASpendingConverter):
    modelclass = Grant
    outfile_basename = 'grants'
    module = faads


    def __init__(self):
        super(Command, self).__init__()

    
    def file_is_right_type(self, file_):
        return 'Contracts' not in file_

