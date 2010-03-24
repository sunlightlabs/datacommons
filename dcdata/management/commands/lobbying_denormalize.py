from dcdata.lobbying.sources.crp import FILE_TYPES, MODELS
from django.core.management.base import CommandError, BaseCommand
from saucebrush.sources import CSVSource
from saucebrush.filters import *
from saucebrush.emitters import DebugEmitter, CSVEmitter
from saucebrush import Recipe, run_recipe
from optparse import make_option
import os

# util functions

def name_proc(standardized, raw):
    return standardized or raw
        
def yn_proc(yn):
    return yn.lower() == 'y'

# denormalization handlers

def lobbying_handler(inpath, outpath, infields, outfields):
    
    run_recipe(
        CSVSource(open(inpath), fieldnames=infields, quotechar='|'),
        FieldRemover('Source'),
        FieldAdder('id', ''),
        FieldAdder('registrant_entity', ''),
        FieldMerger({'registrant_name': ('Registrant','RegistrantRaw')}, name_proc),
        FieldMerger({'registrant_is_firm': ('IsFirm',)}, yn_proc),
        FieldAdder('client_entity', ''),
        FieldAdder('client_parent_entity', ''),
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
            'client_ext_id': 'OrgID',
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
        FieldAdder('lobbyist_entity', ''),
        FieldAdder('candidate_entity', ''),
        FieldMerger({'lobbyist_name': ('Lobbyist','Lobbyist_raw')}, name_proc),
        FieldMerger({'member_of_congress': ('FormerCongMem',)}, yn_proc),
        FieldRenamer({
            'transaction_id': 'Uniqid',
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
        FieldAdder('agency_entity', ''),
        FieldRenamer({
            'transaction_id': 'UniqID',
            'agency_name': 'Agency',
            'agency_ext_id': 'AgencyID',
        }),
        #DebugEmitter(),
        CSVEmitter(open(outpath, 'w'), fieldnames=outfields),
    )

HANDLERS = {
    "lob_lobbying": lobbying_handler,
    "lob_lobbyist": lobbyist_handler,
    "lob_agency": agency_handler,
}

# management command

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option("-d", "--dataroot", dest="dataroot", help="path to data directory", metavar="PATH"),)

    def handle(self, *args, **options):
        
        if 'dataroot' not in options or options['dataroot'] is None:
            raise CommandError("path to dataroot is required")
        
        dataroot = os.path.abspath(options['dataroot'])
    
        for table, infields in FILE_TYPES.iteritems():
            
            handler = HANDLERS.get(table, None)
            
            if handler is not None:
                
                inpath = os.path.join(dataroot, "%s.txt" % table)
                outpath = os.path.join(dataroot, "denorm_%s.csv" % table)
                
                outfields = [field.name for field in MODELS[table]._meta.fields]

                print "Denormalizing %s" % inpath
                
                handler(inpath, outpath, infields, outfields)