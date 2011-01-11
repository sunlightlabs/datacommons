
from saucebrush.filters import FieldAdder, FieldMerger, FieldModifier, FieldRenamer
from saucebrush.emitters import  CSVEmitter, DebugEmitter
from saucebrush.utils import Files
from dcdata.contribution.models import CRP_TRANSACTION_NAMESPACE

import saucebrush

from crp_denormalize import *
from dcdata.processor import chain_filters, load_data
from dcdata.utils.dryrub import FieldCountValidator, CSVFieldVerifier,\
    VerifiedCSVSource


class CommitteeFilter(Filter):
    def __init__(self, committees):
        super(CommitteeFilter, self).__init__()
        self._committees = committees
    def process_record(self, record):
        committee_ext_id = record.get('committee_ext_id', "")
        if committee_ext_id:
            cmte_id = committee_ext_id
            committee = self._committees.get('%s:%s' % (record['cycle'], cmte_id), "")
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
            
        if 'contributor_name' in record:
            record['organization_name'] = record['contributor_name']

        return record
        
        



class CRPDenormalizePac2Pac(CRPDenormalizeBase):
    
    @staticmethod
    def get_record_processor(catcodes, candidates, committees):        
        return chain_filters(
            CSVFieldVerifier(),

            ContribRecipFilter(),
            CommitteeFilter(committees),
            RecipientFilter(candidates, committees),
            
            # transaction filters
            FieldAdder('transaction_namespace', CRP_TRANSACTION_NAMESPACE),
            FieldMerger({'transaction_id': ('cycle','fec_rec_no')}, lambda cycle, fecid: 'pac2pac:%s:%s' % (cycle, fecid), keep_fields=True),
            FieldMerger({'transaction_type': ('type',)}, lambda t: t.strip().lower()),
            
            # filing reference ID
            FieldRenamer({'filing_id': 'microfilm'}),
            
            # date stamp
            FieldModifier('date', parse_date_iso),
            
            # catcode
            FieldMerger({'contributor_category': ('real_code',)}, lambda s: s.upper() if s else "", keep_fields=True),
            FieldMerger({'recipient_category': ('recip_prim_code',)}, lambda s: s.upper() if s else "", keep_fields=True),
            
            FieldRenamer({'contributor_city': 'city',
                          'contributor_state': 'state',
                          'contributor_zipcode': 'zipcode',
                          'contributor_occupation': 'fec_occ_emp',
                          'recipient_party': 'party',}),
            FieldModifier('contributor_state', lambda s: s.strip().upper() if s else ""),
            
            FieldAdder('contributor_type', 'committee'),

            
            # add static fields
            FieldAdder('jurisdiction', 'F'),
            FieldMerger({'is_amendment': ('amend',)}, lambda s: s.strip().upper() != 'N'),

            FieldMerger({'candidacy_status': ('curr_cand', 'cycle_cand')}, lambda curr, cycle: "" if cycle != 'Y' else curr == 'Y' and cycle == 'Y', keep_fields=False ),
            
            # filter through spec
            SpecFilter(SPEC))
        
    def denormalize(self, data_path, cycles, catcodes, candidates, committees):
        infiles = Files(*[os.path.join(data_path, 'raw', 'crp', 'pac_other%s.txt' % cycle) for cycle in cycles])
        outfile = open(os.path.join(data_path, 'denormalized', 'denorm_pac2pac.txt'), 'w')
        
        output_func = CSVEmitter(outfile, fieldnames=FIELDNAMES).process_record
        source = VerifiedCSVSource(infiles, fieldnames=FILE_TYPES['pac_other'], quotechar="|")

        record_processor = self.get_record_processor(catcodes, candidates, committees)

        load_data(source, record_processor, output_func)
        
            
Command = CRPDenormalizePac2Pac            
            
