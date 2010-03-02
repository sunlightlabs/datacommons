
from saucebrush.filters import FieldAdder, FieldMerger, FieldModifier, FieldRenamer
from saucebrush.emitters import  CSVEmitter, DebugEmitter
from saucebrush.sources import CSVSource
from saucebrush.utils import Files
from dcdata.contribution.models import CRP_TRANSACTION_NAMESPACE

import saucebrush

from crp_denormalize import *
from dcdata.processor import chain_filters, load_data




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
                add_candidate_recipient(candidate, record)
            elif recip_id.startswith('C'):
                committee = self._committees.get('%s:%s' % (record['cycle'], recip_id), None)
                add_committee_recipient(committee, record)
        return record
    

class CommitteeFilter(Filter):
    def __init__(self, committees):
        super(CommitteeFilter, self).__init__()
        self._committees = committees
    def process_record(self, record):
        committee_ext_id = record.get('committee_ext_id', None)
        if committee_ext_id:
            cmte_id = committee_ext_id
            committee = self._committees.get('%s:%s' % (record['cycle'], cmte_id), None)
            if committee:
                record['committee_name'] = committee['pac_short']
                record['committee_party'] = committee['party']
        return record
        
        
class ContribRecipFilter(Filter):

    def process_record(self, record):
        
        filer_id = record['filer_id']
        filer_name = record['contrib_lend_trans'].strip()
        other_id = record['other_id']
        trans_type = record['type'].strip().upper()
        if trans_type.startswith('1'):
            record['committee_ext_id'] = filer_id
            record['contributor_name'] = filer_name
            record['contributor_ext_id'] = other_id
        elif trans_type.startswith('2'):
            record['contributor_ext_id'] = filer_id
            record['committee_name'] = filer_name
            record['committee_ext_id'] = other_id
            
        donor_name = record['donor_cmte'].strip()
        if donor_name:
            record['contributor_name'] = donor_name

        return record
        
        



class CRPDenormalizePac2Pac(CRPDenormalizeBase):
    
    @staticmethod
    def get_record_processor(catcodes, candidates, committees):
        def real_code(s):
            s = s.upper()
            if s in catcodes:
                return catcodes[s]['catorder'].upper()        
        
        return chain_filters(
            ContribRecipFilter(),
            CommitteeFilter(committees),
            RecipientFilter(candidates, committees),
            
            # transaction filters
            FieldAdder('transaction_namespace', CRP_TRANSACTION_NAMESPACE),
            FieldMerger({'transaction_id': ('cycle','fec_rec_no')}, lambda cycle, fecid: '%s:%s' % (cycle, fecid), keep_fields=True),
            FieldMerger({'transaction_type': ('type',)}, lambda t: t.strip().lower()),
            
            # filing reference ID
            FieldRenamer({'filing_id': 'microfilm'}),
            
            # date stamp
            FieldModifier('date', parse_date_iso),
            
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
            
            # filter through spec
            SpecFilter(SPEC))
        
    def denormalize(self, data_path, cycles, catcodes, candidates, committees):
        infiles = Files(*[os.path.join(data_path, 'raw', 'crp', 'pac_other%s.csv' % cycle) for cycle in cycles])
        outfile = open(os.path.join(data_path, 'denormalized', 'denorm_pac2pac.csv'), 'w')
        
        source = CSVSource(infiles, fieldnames=FILE_TYPES['pac_other'])
        output_func = CSVEmitter(outfile, fieldnames=FIELDNAMES).process_record

        record_processor = self.get_record_processor(catcodes, candidates, committees)

        load_data(source, record_processor, output_func)
        
            
Command = CRPDenormalizePac2Pac            
            