
from saucebrush.filters import FieldAdder, FieldMerger, FieldModifier, FieldRenamer
from saucebrush.emitters import CSVEmitter
from saucebrush.utils import Files
from dcdata.contribution.models import CRP_TRANSACTION_NAMESPACE
import saucebrush

from crp_denormalize import *
from dcdata.processor import chain_filters, load_data
from optparse import make_option
from dcdata.utils.dryrub import FieldCountValidator, CSVFieldVerifier,\
    VerifiedCSVSource



class Pac2CandRecipientFilter(RecipientFilter):
    def __init__(self, candidates):
        super(Pac2CandRecipientFilter, self).__init__(candidates, {})
    def process_record(self, record):
        cid = record['cid'].upper()
        candidate = self._candidates.get('%s:%s' % (record['cycle'], cid), "")
        self.add_candidate_recipient(candidate, record)
        return record


class ContributorFilter(Filter):
    def __init__(self, committees):
        super(ContributorFilter, self).__init__()
        self._committees = committees
    def process_record(self, record):
        pac_id = record['pac_id'].upper()
        committee = self._committees.get('%s:%s' % (record['cycle'], pac_id), "")
        if committee:
            record['contributor_name'] = committee['pac_short']
            record['organization_name'] = record['contributor_name']
            record['contributor_party'] = committee['party']
        return record


class CRPDenormalizePac2Candidate(CRPDenormalizeBase):
    
    @staticmethod
    def get_record_processor(catcodes, candidates, committees):
        return chain_filters(
            CSVFieldVerifier(),
                             
            # transaction filters
            FieldAdder('transaction_namespace', CRP_TRANSACTION_NAMESPACE),
            FieldMerger({'transaction_id': ('cycle','fec_rec_no')}, lambda cycle, fecid: 'pac2cand:%s:%s' % (cycle, fecid), keep_fields=True),
            FieldMerger({'transaction_type': ('type',)}, lambda t: t.strip().lower()),
            
            # date stamp
            FieldModifier('date', parse_date_iso),
            
            # contributor and recipient fields
            ContributorFilter(committees),
            FieldRenamer({'contributor_ext_id': 'pac_id'}),
            FieldAdder('contributor_type', 'committee'),
            
            Pac2CandRecipientFilter(candidates),
            FieldAdder('recipient_type', 'politician'),
            
            # catcode
            CatCodeFilter('contributor', catcodes),
            
            # add static fields
            FieldAdder('is_amendment', False),

            FieldMerger({'candidacy_status': ('curr_cand', 'cycle_cand')}, lambda curr, cycle: "" if cycle != 'Y' else curr == 'Y' and cycle == 'Y', keep_fields=False ),
            
            # filter through spec
            SpecFilter(SPEC))
            
    def denormalize(self, data_path, cycles, catcodes, candidates, committees):
        input_files = Files(*[os.path.join(data_path, 'raw', 'crp', 'pacs%s.txt' % cycle) for cycle in cycles])
        outfile = open(os.path.join(data_path, 'denormalized', 'denorm_pac2cand.txt'), 'w')
        
        source = VerifiedCSVSource(input_files, fieldnames=FILE_TYPES['pacs'], quotechar="|")
        output_func = CSVEmitter(outfile, fieldnames=FIELDNAMES).process_record
        
        processor_func = self.get_record_processor(catcodes, candidates, committees)

        load_data(source, processor_func, output_func)
            

Command = CRPDenormalizePac2Candidate
            
