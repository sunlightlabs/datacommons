import sys
import logging
import os
from optparse import make_option
from django.core.management.base import CommandError
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from saucebrush.filters import FieldAdder, FieldMerger, FieldModifier, FieldRenamer,\
    Filter
from saucebrush.emitters import CSVEmitter, DebugEmitter
from saucebrush.sources import CSVSource

from dcdata.processor import chain_filters, load_data
from dcdata.contribution.sources.crp import CYCLES, FILE_TYPES
from dcdata.contribution.models import CRP_TRANSACTION_NAMESPACE
from crp_denormalize import *

### Filters



# this list was built by searching for the most frequent organization names in the unfiltered
# contribution data. I went through all organization names with at least 200 entries and entered
# all of the names that weren't organziations. -epg
disallowed_orgnames = set(['retired', 'homemaker', 'attorney', '[24i contribution]', 'self-employed', 
                          'physician', 'self', 'information requested', 'self employed', '[24t contribution]', 
                          'consultant', 'investor', '[candidate contribution]', 'n/a', 'farmer', 'real estate', 
                          'none', 'writer', 'dentist', 'info requested', 'business owner', 'accountant', 
                          'artist', 'rancher', 'student', 'realtor', 'investments', 'real estate developer', 
                          'unemployed', 'requested', 'owner', 'developer', 'businessman', 'contractor', 
                          'president', 'engineer', 'n', 'psychologist', 'real estate broker', 'executive', 
                          'private investor', 'architect', 'sales', 'real estate investor', 'selfemployed', 
                          'philanthropist', 'not employed', 'author', 'builder', 'insurance agent', 'volunteer', 
                          'construction', 'insurance', 'entrepreneur', 'lobbyist', 'ceo', 'n.a', 'actor', 
                          'photographer', 'musician', 'interior designer', 'restaurant owner', 'teacher', 
                          'designer', 'surgeon', 'social worker', 'veterinarian', 'psychiatrist', 'chiropractor', 
                          'auto dealer', 'small business owner', 'optometrist', 'producer', 'business', 
                          '.information requested', 'financial advisor', 'pharmacist', 'psychotherapist', 
                          'manager', 'management consultant', 'general contractor', 'finance', 'orthodontist', 
                          'actress', 'n.a.', 'restauranteur', 'property management', 'home builder', 'oil & gas', 
                          'real estate investments', 'geologist', 'professor', 'farming', 'real estate agent', 
                          'na', 'financial planner', 'community volunteer', 'property manager', 'political consultant', 
                          'public relations', 'business consultant', 'publisher', 'insurance broker', 'educator', 
                          'nurse', 'orthopedic surgeon', 'editor', 'marketing', 'dairy farmer', 'investment advisor', 
                          'freelance writer', 'investment banker', 'trader', 'computer consultant', 'banker', 
                          'oral surgeon', 'business executive', 'unknown', 'civic volunteer', 'filmmaker', 'economist'])


class OrganizationFilter(Filter):
    def process_record(self, record):
        orgname = record.get('org_name', '').strip()
        record['organization_name'] = orgname if orgname and orgname.lower() not in disallowed_orgnames else None
        return record


class CommitteeFilter(Filter):
    def __init__(self, committees):
        super(CommitteeFilter, self).__init__()
        self._committees = committees
    def process_record(self, record):
        cmte_id = record['cmte_id'].upper()
        committee = self._committees.get('%s:%s' % (record['cycle'], cmte_id), None)
        if committee:
            record['committee_name'] = committee['pac_short']
            record['committee_party'] = committee['party']
        return record
 

class CRPDenormalizeIndividual(CRPDenormalizeBase):

    @staticmethod
    def get_record_processor(catcodes, candidates, committees):
        return chain_filters(
                # broken at the moment--can't use anything deriving from YieldFilter
                #FieldCountValidator(len(FILE_TYPES['indivs'])),
        
                # transaction filters
                FieldAdder('transaction_namespace', CRP_TRANSACTION_NAMESPACE),
                FieldMerger({'transaction_id': ('cycle','fec_trans_id')}, lambda cycle, fecid: '%s:%s' % (cycle, fecid), keep_fields=True),
                FieldMerger({'transaction_type': ('type',)}, lambda t: t.strip().lower() if t else '', keep_fields=True),
        
                # filing reference ID
                FieldRenamer({'filing_id': 'microfilm'}),
        
                # date stamp
                FieldModifier('date', parse_date_iso),
        
                # rename contributor, organization, and parent_organization fields
                FieldRenamer({'contributor_name': 'contrib',
                          'parent_organization_name': 'ult_org',}),
         
                RecipientFilter(candidates, committees),
                CommitteeFilter(committees),
                OrganizationFilter(),
        
                # create URNs
                FieldRenamer({'contributor_ext_id': 'contrib_id', 'committee_ext_id': 'cmte_id'}),
        
                # address and gender fields
                FieldRenamer({'contributor_address': 'street',
                          'contributor_city': 'city',
                          'contributor_state': 'state',
                          'contributor_zipcode': 'zipcode',
                          'contributor_gender': 'gender'}),
                FieldModifier('contributor_state', lambda s: s.upper() if s else None),
                FieldModifier('contributor_gender', lambda s: s.upper() if s else None),
        
                # employer/occupation filter
                FECOccupationFilter(),
        
                # catcode
                CatCodeFilter('contributor', catcodes),
        
                # add static fields
                FieldAdder('contributor_type', 'individual'),
                FieldAdder('is_amendment', False),
                FieldAdder('election_type', 'G'),
        
                # filter through spec
                SpecFilter(SPEC))
        
    
    def denormalize(self, data_path, cycles, catcodes, candidates, committees):
        record_processor = self.get_record_processor(catcodes, candidates, committees)   
           
        for cycle in cycles:
            in_path = os.path.join(data_path, 'raw', 'crp', 'indivs%s.csv' % cycle)
            infile = open(in_path, 'r')
            out_path = os.path.join(data_path, 'denormalized', 'denorm_indivs.%s.csv' % cycle)
            outfile = open(out_path, 'w')
    
            sys.stdout.write('Reading from %s, writing to %s...\n' % (in_path, out_path))
    
            input_source = CSVSource(infile, fieldnames=FILE_TYPES['indivs'])
            output_func = CSVEmitter(outfile, fieldnames=FIELDNAMES).process_record
    
            load_data(input_source, record_processor, output_func)
       
       
Command = CRPDenormalizeIndividual         
    
