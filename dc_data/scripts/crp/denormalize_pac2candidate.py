from dcdata.contribution.sources.crp import CYCLES, FILE_TYPES
from dcdata.utils.dryrub import CountEmitter
from saucebrush.filters import Filter, FieldAdder, FieldCopier, FieldMerger, FieldModifier, FieldRemover, FieldRenamer
from saucebrush.emitters import Emitter, CSVEmitter, DebugEmitter
from saucebrush.sources import CSVSource
from saucebrush.utils import Files
import datetime
import logging
import os
import saucebrush

from denormalize import FIELDNAMES, load_catcodes, parse_date_iso, SpecFilter, FECOccupationFilter

#####

def main():

    from optparse import OptionParser

    usage = "usage: %prog [options]"

    parser = OptionParser(usage=usage)
    parser.add_option("-c", "--cycles", dest="cycles",
                      help="cycles to load ex: 90,92,08", metavar="CYCLES")
    parser.add_option("-d", "--dataroot", dest="dataroot",
                      help="path to data directory", metavar="PATH")
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose", default=False,
                      help="noisy output")

    (options, args) = parser.parse_args()

    if not options.dataroot:
        parser.error("path to dataroot is required")

    cycles = []
    if options.cycles:
        for cycle in options.cycles.split(','):
            if len(cycle) == 4:
                cycle = cycle[2:4]
            if cycle in CYCLES:
                cycles.append(cycle)
    else:
        cycles = CYCLES

    dataroot = os.path.abspath(options.dataroot)
    tmppath = os.path.join(dataroot, 'tmp')
    if not os.path.exists(tmppath):
        os.makedirs(tmppath)

    catcodes = load_catcodes(dataroot)
    
    emitter = CSVEmitter(open(os.path.join(tmppath, 'denorm_pac2cand.csv'), 'w'), fieldnames=FIELDNAMES)

    files = Files(*[os.path.join(dataroot, 'raw', 'crp', 'pacs%s.csv' % cycle) for cycle in cycles])
    
    spec = dict(((fn, None) for fn in FIELDNAMES))
    
    def candidate_urn(s):
        return 'urn:crp:candidate:%s' % s.strip().upper() if s else None
    
    def committee_urn(s):
        return 'urn:crp:committee:%s' % s.strip().upper() if s else None
    
    saucebrush.run_recipe(
        
        # load source
        CSVSource(files, fieldnames=FILE_TYPES['pacs']),
        
        # transaction filters
        FieldAdder('transaction_namespace', 'urn:fec:transaction'),
        FieldMerger({'transaction_id': ('cycle','fec_rec_no')}, lambda cycle, fecid: 'FEC:%s:%s' % (cycle, fecid), keep_fields=True),
        FieldMerger({'transaction_type': ('type',)}, lambda t: t.strip().lower()),
        
        # date stamp
        FieldModifier('datestamp', parse_date_iso),
        
        # contributor and recipient fields
        FieldMerger({'contributor_urn': ('pac_id',)}, committee_urn),
        FieldAdder('contributor_type', 'committee'),
        FieldMerger({'recipient_urn': ('cid',)}, candidate_urn),
        FieldAdder('recipient_type', 'politician'),
        
        # catcode
        FieldMerger({'contributor_category': ('real_code',)}, lambda s: s.upper() if s else None, keep_fields=True),
        FieldMerger({'contributor_category_order': ('real_code',)}, lambda s: catcodes[s.upper()]['catorder'].upper(), keep_fields=True),
        
        # add static fields
        FieldAdder('is_amendment', False),
        FieldAdder('election_type', 'G'),
        
        # filter through spec
        SpecFilter(spec),
        
        #DebugEmitter(),
        CountEmitter(every=100),
        emitter,
        
    )


if __name__ == "__main__":

    logging.basicConfig(level=logging.DEBUG)

    main()