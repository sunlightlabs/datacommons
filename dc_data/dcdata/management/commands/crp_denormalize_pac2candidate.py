
from dcdata.utils.dryrub import CountEmitter
from saucebrush.filters import FieldAdder, FieldMerger, FieldModifier, FieldRenamer
from saucebrush.emitters import CSVEmitter
from saucebrush.sources import CSVSource
from saucebrush.utils import Files
from dcdata.contribution.models import CRP_TRANSACTION_NAMESPACE
import saucebrush

from crp_denormalize import *
from dcdata.processor import chain_filters, load_data
from optparse import make_option


class RecipCodeFilter(Filter):
    def __init__(self):
        super(RecipCodeFilter, self).__init__()
    def process_record(self, record):
        if record['recip_code']:
            recip_code = record['recip_code'].strip().upper()
            record['recipient_party'] = recip_code[0]
            record['seat_result'] = recip_code[1] if recip_code[1] in ('W','L') else None
        return record


class RecipientFilter(Filter):
    def __init__(self, candidates):
        super(RecipientFilter, self).__init__()
        self._candidates = candidates
    def process_record(self, record):
        cid = record['cid'].upper()
        candidate = self._candidates.get('%s:%s' % (record['cycle'], cid), None)
        if candidate:
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
            result = candidate.get('recip_code', '').strip().upper()
            if result and result[1] in ('W','L'):
                record['seat_result'] = result[1]
                
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
            FieldRenamer({'recipient_ext_id': 'cid'}),
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
            