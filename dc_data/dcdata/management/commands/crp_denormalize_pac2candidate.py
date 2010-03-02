
from saucebrush.filters import FieldAdder, FieldMerger, FieldModifier, FieldRenamer
from saucebrush.emitters import CSVEmitter
from saucebrush.sources import CSVSource
from saucebrush.utils import Files
from dcdata.contribution.models import CRP_TRANSACTION_NAMESPACE
import saucebrush

from crp_denormalize import *
from dcdata.processor import chain_filters, load_data
from optparse import make_option





class RecipientFilter(Filter):
    def __init__(self, candidates):
        super(RecipientFilter, self).__init__()
        self._candidates = candidates
    def process_record(self, record):
        cid = record['cid'].upper()
        candidate = self._candidates.get('%s:%s' % (record['cycle'], cid), None)
        add_candidate_recipient(candidate, record)
        return record


class ContributorFilter(Filter):
    def __init__(self, committees):
        super(ContributorFilter, self).__init__()
        self._committees = committees
    def process_record(self, record):
        pac_id = record['pac_id'].upper()
        committee = self._committees.get('%s:%s' % (record['cycle'], pac_id), None)
        if committee:
            record['contributor_name'] = committee['pac_short']
            record['contributor_party'] = committee['party']
            record['contributor_type'] = 'committee'
        return record


class CRPDenormalizePac2Candidate(CRPDenormalizeBase):
    
    @staticmethod
    def get_record_processor(catcodes, candidates, committees):
        return chain_filters(
            # transaction filters
            FieldAdder('transaction_namespace', CRP_TRANSACTION_NAMESPACE),
            FieldMerger({'transaction_id': ('cycle','fec_rec_no')}, lambda cycle, fecid: '%s:%s' % (cycle, fecid), keep_fields=True),
            FieldMerger({'transaction_type': ('type',)}, lambda t: t.strip().lower()),
            
            # date stamp
            FieldModifier('date', parse_date_iso),
            
            # contributor and recipient fields
            ContributorFilter(committees),
            FieldRenamer({'contributor_ext_id': 'pac_id'}),
            FieldAdder('contributor_type', 'committee'),
            
            RecipientFilter(candidates),
            FieldAdder('recipient_type', 'politician'),
            
            # catcode
            CatCodeFilter('contributor', catcodes),
            
            # add static fields
            FieldAdder('is_amendment', False),
            FieldAdder('election_type', 'G'),
            
            # filter through spec
            SpecFilter(SPEC))
            
    def denormalize(self, data_path, cycles, catcodes, candidates, committees):
        input_files = Files(*[os.path.join(data_path, 'raw', 'crp', 'pacs%s.csv' % cycle) for cycle in cycles])
        outfile = open(os.path.join(data_path, 'denormalized', 'denorm_pac2cand.csv'), 'w')
        
        source = CSVSource(input_files, fieldnames=FILE_TYPES['pacs'])
        output_func = CSVEmitter(outfile, fieldnames=FIELDNAMES).process_record
        
        processor_func = self.get_record_processor(catcodes, candidates, committees)

        load_data(source, processor_func, output_func)
            

Command = CRPDenormalizePac2Candidate
            