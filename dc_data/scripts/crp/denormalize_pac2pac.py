from dcdata.utils.dryrub import CountEmitter
from saucebrush.filters import FieldAdder, FieldMerger, FieldModifier, FieldRenamer
from saucebrush.emitters import  CSVEmitter, DebugEmitter
from saucebrush.sources import CSVSource
from saucebrush.utils import Files

import saucebrush

from denormalize import *


class RecipientFilter(Filter):
    def __init__(self, candidates, committees):
        super(RecipientFilter, self).__init__()
        self._candidates = candidates
        self._committees = committees
    def process_record(self, record):
        recip_id = record['recip_id'].strip().upper()
        if recip_id:
            if recip_id.startswith('N'):
                candidate = self._candidates.get('%s:%s' % (record['cycle'], recip_id), None)
                if candidate:
                    record['recipient_urn'] = candidate_urn(recip_id)
                    record['recipient_name'] = candidate['first_last_p']
                    record['recipient_party'] = candidate['party']
                    record['recipient_type'] = 'politician'
                    record['seat_status'] = candidate['crp_ico']
                    seat = candidate['dist_id_run_for'].upper()
                    if len(seat) == 4:
                        if seat == 'PRES':
                            record['seat'] = 'federal:president'
                        else:
                            if seat[2] == 'S':
                                record['seat'] = 'federal:senate'
                            else:
                                record['seat'] = 'federal:house'
                                record['district'] = "%s-%s" % (seat[:2], seat[2:])
            elif recip_id.startswith('C'):
                committee = self._committees.get('%s:%s' % (record['cycle'], recip_id), None)
                record['recipient_urn'] = committee_urn(recip_id)
                if committee:
                    record['recipient_name'] = committee['pac_short']
                    record['recipient_party'] = committee['party']
                    record['recipient_type'] = 'committee'
                else:
                    print "no committee for %s" % recip_id
            else:
                print "!!!!!!!!!! invalid recipient %s" % recip_id
        return record


class CommitteeFilter(Filter):
    def __init__(self, committees):
        super(CommitteeFilter, self).__init__()
        self._committees = committees
    def process_record(self, record):
        committee_urn = record.get('committee_urn', None)
        if committee_urn:
            cmte_id = committee_urn.rsplit(":", 1)[1]
            committee = self._committees.get('%s:%s' % (record['cycle'], cmte_id), None)
            if committee:
                record['committee_name'] = committee['pac_short']
                record['committee_party'] = committee['party']
        return record
        
        
class ContribRecipFilter(Filter):

    def process_record(self, record):
        
        filer_urn = committee_urn(record['filer_id'])
        filer_name = record['contrib_lend_trans'].strip()
        other_urn = committee_urn(record['other_id'])
        trans_type = record['type'].strip().upper()
        if trans_type.startswith('1'):
            record['committee_urn'] = filer_urn
            record['contributor_name'] = filer_name
            record['contributor_urn'] = other_urn
        elif trans_type.startswith('2'):
            record['contributor_urn'] = filer_urn
            record['committee_name'] = filer_name
            record['committee_urn'] = other_urn
            
        donor_name = record['donor_cmte'].strip()
        if donor_name:
            record['contributor_name'] = donor_name

        return record
        
        
class RecipCodeFilter(Filter):
    def process_record(self, record):
        if record['recip_code']:
            recip_code = record['recip_code'].strip().upper()
            record['seat_result'] = recip_code[1] if recip_code[1] in ('W','L') else None
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

    (options, _) = parser.parse_args()

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
    tmppath = os.path.join(dataroot, 'denormalized')
    if not os.path.exists(tmppath):
        os.makedirs(tmppath)
    
    outfile = open(os.path.join(tmppath, 'denorm_pac2pac.csv'), 'w')

    infiles = Files(*[os.path.join(dataroot, 'raw', 'crp', 'pac_other%s.csv' % cycle) for cycle in cycles])

    print "Loading catcodes..."
    catcodes = load_catcodes(dataroot)
    
    print "Loading candidates..."
    candidates = load_candidates(dataroot)
    
    print "Loading committees..."
    committees = load_committees(dataroot)
    
    run_denormalization(infiles, outfile, catcodes, candidates, committees)
    

def run_denormalization(infile, outfile, catcodes, candidates, committees):
    def real_code(s):
        s = s.upper()
        if s in catcodes:
            return catcodes[s]['catorder'].upper()
        
    saucebrush.run_recipe(
        # load sources
        CSVSource(infile, fieldnames=FILE_TYPES['pac_other']),
        
        ContribRecipFilter(),
        CommitteeFilter(committees),
        RecipientFilter(candidates, committees),
        
        # transaction filters
        FieldAdder('transaction_namespace', 'urn:fec:transaction'),
        FieldMerger({'transaction_id': ('cycle','fec_rec_no')}, lambda cycle, fecid: 'FEC:%s:%s' % (cycle, fecid), keep_fields=True),
        FieldMerger({'transaction_type': ('type',)}, lambda t: t.strip().lower()),
        
        # filing reference ID
        FieldRenamer({'filing_id': 'microfilm'}),
        
        # date stamp
        FieldModifier('datestamp', parse_date_iso),
        
        # catcode
        FieldMerger({'contributor_category': ('real_code',)}, lambda s: s.upper() if s else None, keep_fields=True),
        FieldMerger({'contributor_category_order': ('real_code',)}, real_code, keep_fields=True),
        FieldMerger({'recipient_category': ('recip_prim_code',)}, lambda s: s.upper() if s else None, keep_fields=True),
        FieldMerger({'recipient_category_order': ('recip_prim_code',)}, real_code, keep_fields=True),
        
        FieldRenamer({'contributor_city': 'city',
                      'contributor_state': 'state',
                      'contributor_zipcode': 'zipcode',
                      'contributor_occupation': 'fec_occ_emp',
                      'recipient_party': 'party',}),
        FieldModifier('contributor_state', lambda s: s.strip().upper() if s else None),
        
        FieldAdder('contributor_type', 'committee'),
        
        # add static fields
        FieldAdder('jurisdiction', 'F'),
        FieldMerger({'is_amendment': ('amend',)}, lambda s: s.strip().upper() != 'N'),
        FieldAdder('election_type', 'G'),
        
        # recip_code
        RecipCodeFilter(),
        
        # filter through spec
        SpecFilter(SPEC),
        
        #DebugEmitter(),
        CountEmitter(every=1000),
        CSVEmitter(outfile, fieldnames=FIELDNAMES),
    )


if __name__ == "__main__":

    logging.basicConfig(level=logging.DEBUG)

    main()