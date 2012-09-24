from dcdata.lobbying.models import Lobbying, Lobbyist, Issue, Bill, Agency
from dcdata.management.base.importer import BaseImporter
from saucebrush.sources import CSVSource
from saucebrush.filters import FieldMerger, FieldRemover, FieldRenamer, \
        FieldAdder, FieldModifier
from saucebrush.emitters import CSVEmitter
from saucebrush import run_recipe
import os, os.path

# util functions

def name_proc(standardized, raw):
    if standardized or raw:
        return (standardized or raw).strip()

def yn_proc(yn):
    return yn.lower() == 'y'

# denormalization handlers

def lobbying_handler(inpath, outpath, infields, outfields):

    run_recipe(
        CSVSource(open(inpath), fieldnames=infields, quotechar='|'),
        FieldRemover('Source'),
        FieldMerger({'registrant_name': ('Registrant','RegistrantRaw')}, name_proc),
        FieldMerger({'registrant_is_firm': ('IsFirm',)}, yn_proc),
        FieldMerger({'client_name': ('Client','Client_raw')}, name_proc),
        FieldMerger({'amount': ('Amount',)}, lambda x: float(x or 0)),
        FieldMerger({'affiliate': ('Affiliate',)}, yn_proc),
        FieldMerger({'filing_included_nsfs': ('IncludeNSFS',)}, yn_proc),
        FieldMerger({'include_in_industry_totals': ('Ind',)}, yn_proc),
        FieldMerger({'use': ('Use',)}, yn_proc),
        FieldRenamer({
            'transaction_id': 'Uniqid',
            'transaction_type': 'Type',
            'transaction_type_desc': 'TypeLong',
            'year': 'Year',
            'client_category': 'Catcode',
            'client_parent_name': 'Ultorg',
            'filing_type': 'Self',
        }),
        #DebugEmitter(),
        CSVEmitter(open(outpath, 'w'), fieldnames=outfields),
    )

def lobbyist_handler(inpath, outpath, infields, outfields):

    run_recipe(
        CSVSource(open(inpath), fieldnames=infields, quotechar='|'),
        FieldAdder('id', ''),
        FieldMerger({'lobbyist_name': ('Lobbyist','Lobbyist_raw')}, name_proc),
        FieldMerger({'member_of_congress': ('FormerCongMem',)}, yn_proc),
        FieldRenamer({
            'transaction': 'Uniqid',
            'year': 'Year',
            'lobbyist_ext_id': 'LobbyistID',
            'candidate_ext_id': 'CID',
            'government_position': 'OfficalPos',
        }),
        #DebugEmitter(),
        CSVEmitter(open(outpath, 'w'), fieldnames=outfields),
    )

def agency_handler(inpath, outpath, infields, outfields):

    run_recipe(
        CSVSource(open(inpath), fieldnames=infields, quotechar='|'),
        FieldAdder('id', ''),
        FieldRenamer({
            'transaction': 'UniqID',
            'agency_name': 'Agency',
            'agency_ext_id': 'AgencyID',
        }),
        #DebugEmitter(),
        CSVEmitter(open(outpath, 'w'), fieldnames=outfields),
    )

def issue_handler(inpath, outpath, infields, outfields):

    run_recipe(
        CSVSource(open(inpath), fieldnames=infields, quotechar='|'),
        FieldRenamer({
            'id': 'SI_ID',
            'transaction': 'UniqID',
            'general_issue_code': 'IssueID',
            'general_issue': 'Issue',
            'specific_issue': 'SpecIssue',
            'year': 'Year',
        }),
        FieldModifier(('general_issue', 'specific_issue'), lambda x: x.replace('\n', ' ')),
        #DebugEmitter(),
        CSVEmitter(open(outpath, 'w'), fieldnames=outfields),
    )

def bills_handler(inpath, outpath, infields, outfields):

    run_recipe(
        CSVSource(open(inpath), fieldnames=infields, quotechar='|'),
        FieldAdder('id', ''),
        FieldRenamer({
            'bill_id':     'B_ID',
            'issue':       'SI_ID',
            'congress_no': 'CongNo',
            'bill_name':   'Bill_Name',
        }),
        #DebugEmitter(),
        CSVEmitter(open(outpath, 'w'), fieldnames=outfields),
    )

HANDLERS = {
    "lob_lobbying": lobbying_handler,
    "lob_lobbyist": lobbyist_handler,
    "lob_agency": agency_handler,
    "lob_issue": issue_handler,
    "lob_bills": bills_handler,
}

FILE_TYPES = {
    "lob_lobbying": ('Uniqid','RegistrantRaw','Registrant','IsFirm',
                     'Client_raw','Client','Ultorg','Amount','Catcode',
                     'Source','Self','IncludeNSFS','Use','Ind','Year',
                     'Type','TypeLong','OrgID','Affiliate'),
    "lob_lobbyist": ('Uniqid','Lobbyist_raw','Lobbyist','LobbyistID',
                     'Year','OfficalPos','CID','FormerCongMem'),
    "lob_agency": ('UniqID','AgencyID','Agency'),
    # "lob_indus": ('Ultorg','Client','Total','Year','Catcode'),
    "lob_issue": ('SI_ID','UniqID','IssueID','Issue','SpecIssue','Year'),
    "lob_bills": ('B_ID','SI_ID','CongNo','Bill_Name'),
    # "lob_rpt": ('TypeLong','Typecode'),
}

MODELS = {
    "lob_lobbying": Lobbying,
    "lob_lobbyist": Lobbyist,
    "lob_agency": Agency,
    "lob_issue": Issue,
    "lob_bills": Bill,
}
# management command

class Command(BaseImporter):

    IN_DIR       = '/home/datacommons/data/auto/lobbying/raw/IN'
    DONE_DIR     = '/home/datacommons/data/auto/lobbying/raw/DONE'
    REJECTED_DIR = '/home/datacommons/data/auto/lobbying/raw/REJECTED'
    OUT_DIR      = '/home/datacommons/data/auto/lobbying/denormalized/IN'

    FILE_PATTERN = 'lob_*.txt'


    def do_for_file(self, file_path):
        self.log.info('Starting {0}...'.format(file_path))
        table = os.path.basename(file_path).split('.')[0]

        if FILE_TYPES.has_key(table):
            handler = HANDLERS.get(table, None)
            infields = FILE_TYPES[table]

            if handler is not None:

                inpath = os.path.join(self.IN_DIR, "%s.txt" % table)
                outpath = os.path.join(self.OUT_DIR, "denorm_%s.csv" % table)

                outfields = [field.name for field in MODELS[table]._meta.fields]

                self.log.info("Denormalizing {0}".format(inpath))
                handler(inpath, outpath, infields, outfields)

                self.log.info("Done with {0}.".format(inpath))

        self.archive_file(file_path, timestamp=True)

