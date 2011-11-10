from dcdata.management.base.usaspending_importer import BaseUSASpendingConverter
from dcdata.contracts.models import Contract
from dcdata.scripts.usaspending import fpds


class Command(BaseUSASpendingConverter):
    IN_DIR =       '/home/usaspending/usaspending/latest/datafeeds'
    DONE_DIR =     '/home/usaspending/usaspending/latest/datafeeds/DONE'
    REJECTED_DIR = '/home/usaspending/usaspending/latest/datafeeds/REJECTED'
    OUT_DIR =      '/home/usaspending/usaspending/latest/datafeeds/OUT'
    FILE_PATTERN = '*_All_Contracts_Full_*.csv' # bash-style, ala '*.sql'

    modelclass = Contract
    outfile_basename = 'contracts'
    module = fpds

    def __init__(self):
        super(Command, self).__init__()

