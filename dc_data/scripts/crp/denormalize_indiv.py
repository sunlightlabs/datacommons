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

### Filters

class RecipCodeFilter(Filter):
    def __init__(self):
        super(RecipCodeFilter, self).__init__()
    def process_record(self, record):
        if record['recip_id'].startswith('N'):
            if record['recip_code']:
                recip_code = record['recip_code'].strip().upper()
                record['recipient_party'] = recip_code[0]
                record['seat_result'] = recip_code[1] if recip_code[1] in ('W','L') else None
        return record

class OrganizationFilter(Filter):
    def process_record(self, record):
        orgname = record.get('org_name', '').strip()
        if not orgname:
            orgname = record.get('emp_ef', '').strip()
            if not orgname and '/' in record['fec_occ_emp']:
                (emp, occ) = record['fec_occ_emp'].split('/', 1)
                orgname = emp.strip()
        record['organization_name'] = orgname or None
        return record

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
    
    emitter = CSVEmitter(open(os.path.join(tmppath, 'denorm_indivs.csv'), 'w'), fieldnames=FIELDNAMES)

    files = Files(*[os.path.join(dataroot, 'raw', 'crp', 'indivs%s.csv' % cycle) for cycle in cycles])
    
    spec = dict(((fn, None) for fn in FIELDNAMES))
    
    # urn methods
    
    def recipient_urn(s):
        if s.startswith('N'):
            return 'urn:crp:candidate:%s' % s.strip().upper()
        elif s.startswith('C'):
            return 'urn:crp:committee:%s' % s.strip().upper()
        return None
    
    def contributor_urn(s):
        return 'urn:crp:individual:%s' % s.strip().upper() if s else None
    
    def committee_urn(s):
        return 'urn:crp:committee:%s' % s.strip().upper() if s else None
        
    # recipient type
    
    def recipient_type(s):
        if s:
            if s.startswith('N'):
                return 'politician'
            elif s.startswith('C'):
                return 'committee'
    
    #
    # main recipe
    #
    
    saucebrush.run_recipe(
        
        # load source
        CSVSource(files, fieldnames=FILE_TYPES['indivs']),
        
        # transaction filters
        FieldAdder('transaction_namespace', 'urn:fec:transaction'),
        FieldMerger({'transaction_id': ('cycle','fec_trans_id')}, lambda cycle, fecid: '%s:%s' % (cycle, fecid), keep_fields=True),
        FieldMerger({'transaction_type': ('type',)}, lambda t: t.strip().lower(), keep_fields=True),
        
        # filing reference ID
        FieldRenamer({'filing_id': 'microfilm'}),
        
        # date stamp
        FieldModifier('datestamp', parse_date_iso),
        
        # rename contributor, organization, and parent_organization fields
        FieldRenamer({'contributor_name': 'contrib',
                      'parent_organization_name': 'ult_org',}),
                      
        OrganizationFilter(),
        
        # create URNs
        FieldMerger({'contributor_urn': ('contrib_id',)}, contributor_urn, keep_fields=True),
        FieldMerger({'recipient_urn': ('recip_id',)}, recipient_urn, keep_fields=True),
        FieldMerger({'committee_urn': ('cmte_id',)}, committee_urn, keep_fields=True),
        
        # recipient type
        FieldMerger({'recipient_type': ('recip_id',)}, recipient_type, keep_fields=True),
        
        # recip code filter
        RecipCodeFilter(),  # recipient party
                            # seat result
        
        # address and gender fields
        FieldRenamer({'contributor_address': 'street',
                      'contributor_city': 'city',
                      'conitrbutor_zipcode': 'zipcode'}),
        FieldModifier('contributor_state', lambda s: s.upper() if s else None),
        FieldModifier('contributor_gender', lambda s: s.upper() if s else None),
        
        # employer/occupation filter
        FECOccupationFilter(),
        
        # catcode
        #FieldMerger({'industry': ('real_code',)}, lambda s: s[0].upper() if s else None, keep_fields=True),
        #FieldMerger({'sector': ('real_code',)}, lambda s: s[:2].upper() if s else None, keep_fields=True),
        FieldMerger({'contributor_category': ('real_code',)}, lambda s: s.upper() if s else None, keep_fields=True),
        FieldMerger({'contributor_category_order': ('real_code',)}, lambda s: catcodes[s.upper()]['catorder'].upper(), keep_fields=True),
        
        # add static fields
        FieldAdder('contributor_type', 'individual'),
        FieldAdder('is_amendment', False),
        FieldAdder('election_type', 'G'),
        
        # filter through spec
        SpecFilter(spec),
        
        DebugEmitter(),
        CountEmitter(every=100),
        #emitter,
        
    )        

if __name__ == "__main__":

    logging.basicConfig(level=logging.DEBUG)

    main()
    
