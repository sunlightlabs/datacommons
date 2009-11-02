from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ImproperlyConfigured
from dcdata.contribution.models import Contribution
from dcdata.loading import Loader, LoaderEmitter, model_fields, BooleanFilter, FloatFilter, IntFilter, ISODateFilter, EntityFilter
from saucebrush.emitters import DebugEmitter
from saucebrush.filters import FieldRemover, FieldAdder
from saucebrush.sources import CSVSource
import saucebrush
import os

class ContributionLoader(Loader):
    
    model = Contribution
    
    def __init__(self, *args, **kwargs):
        super(ContributionLoader, self).__init__(*args, **kwargs)
        
    def _get_instance(self, record):
        key = record['transaction_id']
        namespace = record['transaction_namespace']
        try:
            return Contribution.objects.get(transaction_namespace=namespace, transaction_id=key)
        except Contribution.DoesNotExist:
            return Contribution(transaction_namespace=namespace, transaction_id=key)
        

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
            
            # do resolving of entity fields here
            
            EntityFilter('contributor_entity'),
            EntityFilter('organization_entity'),
            EntityFilter('parent_organization_entity'),
            EntityFilter('recipient_entity'),
            EntityFilter('committee_entity'),
            
            DebugEmitter(),
            #LoaderEmitter(loader),
        )
