from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ImproperlyConfigured
from dcdata.contribution.models import Contribution
from dcdata.loading import Loader, LoaderEmitter, model_fields, BooleanFilter, FloatFilter, IntFilter, ISODateFilter, EntityFilter
from saucebrush.emitters import DebugEmitter
from saucebrush.filters import FieldRemover, FieldAdder, Filter
from saucebrush.sources import CSVSource
import saucebrush
import os

#
# entity filters
#

class ContributorFilter(Filter):
    type_mapping = {'individual': 'I', 'committee': 'C'}
    def process_record(self, record):
        record['contributor_type'] = self.type_mapping.get(record['contributor_type'], None)
        record['contributor_entity'] = None
        return record

class OrganizationFilter(Filter):
    def process_record(self, record):
        record['organization_entity'] = None
        return record

class ParentOrganizationFilter(Filter):
    def process_record(self, record):
        record['parent_organization_entity'] = None
        return record

class RecipientFilter(Filter):
    type_mapping = {'politician': 'P', 'committee': 'C'}
    def process_record(self, record):
        record['recipient_type'] = self.type_mapping.get(record['recipient_type'], None)
        record['recipient_entity'] = None
        return record

class CommitteeFilter(Filter):    
    def process_record(self, record):
        record['committee_entity'] = None
        return record
    
#
# model loader
#

class ContributionLoader(Loader):
    
    model = Contribution
    
    def __init__(self, *args, **kwargs):
        super(ContributionLoader, self).__init__(*args, **kwargs)
        
    def get_instance(self, record):
        key = record['transaction_id']
        namespace = record['transaction_namespace']
        try:
            return Contribution.objects.get(transaction_namespace=namespace, transaction_id=key)
        except Contribution.DoesNotExist:
            return Contribution(transaction_namespace=namespace, transaction_id=key)
    
    def resolve(self, record, obj):
        """ how should an existing record be updated? 
        """
        self.copy_fields(record, obj)
        

class Command(BaseCommand):

    help = "load contributions from csv"
    args = ""

    requires_model_validation = False
    
    def handle(self, csvpath, *args, **options):
        
        fieldnames = model_fields('contribution.Contribution')
        
        loader = ContributionLoader(
            source='CRP',
            description='load from denormalized CSVs',
            imported_by="loadcontributions.py (%s)" % os.getenv('LOGNAME', 'unknown'),
        )
        
        saucebrush.run_recipe(
        
            CSVSource(open(os.path.abspath(csvpath)), fieldnames, skiprows=1),
            
            FieldRemover('id'),
            FieldAdder('import_reference', loader.import_session),
            
            IntFilter('cycle'),
            ISODateFilter('datestamp'),
            BooleanFilter('is_amendment'),
            FloatFilter('amount'),
            
            ContributorFilter(),
            OrganizationFilter(),
            ParentOrganizationFilter(),
            RecipientFilter(),
            CommitteeFilter(),
            
            #DebugEmitter(),
            LoaderEmitter(loader),
            
        )
