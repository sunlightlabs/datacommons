from dcdata.management.base.usaspending_importer import BaseUSASpendingConverter
from dcdata.contracts.models import Contract
from dcdata.scripts.usaspending import fpds


class Command(BaseUSASpendingConverter):
    modelclass = Contract
    outfile_basename = 'contracts'
    module = fpds

    def __init__(self):
        super(Command, self).__init__()


    def file_is_right_type(self, file_):
        return 'Contracts' in file_

