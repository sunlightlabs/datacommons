from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ImproperlyConfigured
from django.db import transaction
from dcdata.contribution.models import Contribution
from dcdata.loading import Loader, LoaderEmitter, model_fields, BooleanFilter, FloatFilter, IntFilter, ISODateFilter, EntityFilter
from dcdata.utils.dryrub import CountEmitter, MD5Filter
from saucebrush.emitters import DebugEmitter
from saucebrush.filters import FieldRemover, FieldAdder, Filter
from saucebrush.sources import CSVSource
from strings.normalizer import basic_normalizer
import saucebrush
import os
import sys

MATCHBOX_ORG_NAMESPACE = 'urn:matchbox:organization:'


#
# entity filters
#

class ContributorFilter(Filter):
    type_mapping = {'individual': 'I', 'committee': 'C', 'organization': 'O'}
    def process_record(self, record):
        record['contributor_type'] = self.type_mapping.get(record['contributor_type'], None)
        #record['contributor_entity'] = None
        return record

class OrganizationFilter(Filter):
    def process_record(self, record):
        return record

class ParentOrganizationFilter(Filter):
    def process_record(self, record):
        return record

class RecipientFilter(Filter):
    type_mapping = {'politician': 'P', 'committee': 'C'}
    def process_record(self, record):
        record['recipient_type'] = self.type_mapping.get(record['recipient_type'], None)
        return record

class CommitteeFilter(Filter):    
    def process_record(self, record):
        return record
    

    
def urn_with_name_fallback(urn_field, name_field):
    def source(record):
        if record.get(urn_field, False):
            return record[urn_field]
        if record.get(name_field, False):
            return 'urn:matchbox:name:' + basic_normalizer(record[name_field].decode('utf-8', 'ignore'))
        return None
    
    return source
    

class AbortFilter(Filter):
    def __init__(self, threshold=0.1):
        self._record_count = 0
        self._threshold = threshold
    def process_record(self, record):
        self._record_count += 1
        if self._record_count > 50:
            reject_count = len(self._recipe.rejected)
            ratio = float(reject_count) / float(self._record_count)
            if ratio > self._threshold:
                for reject in self._recipe.rejected:
                    sys.stderr.write(repr(reject) + '\n')
                raise Exception('Abort: %s of %s records contained errors' % (reject_count, self._record_count))
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
        # try:
        #             return Contribution.objects.get(transaction_namespace=namespace, transaction_id=key)
        #         except Contribution.DoesNotExist:
        #             return Contribution(transaction_namespace=namespace, transaction_id=key)
        return Contribution(transaction_namespace=namespace, transaction_id=key)
    
    def resolve(self, record, obj):
        """ how should an existing record be updated? 
        """
        self.copy_fields(record, obj)
        

class Command(BaseCommand):

    help = "load contributions from csv"
    args = ""

    requires_model_validation = False
    
    @transaction.commit_on_success
    def handle(self, csvpath, *args, **options):
        
        fieldnames = model_fields('contribution.Contribution')
        
        loader = ContributionLoader(
            source='CRP',
            description='load from denormalized CSVs',
            imported_by="loadcontributions.py (%s)" % os.getenv('LOGNAME', 'unknown'),
        )
        
        try:
            saucebrush.run_recipe(
            
                CSVSource(open(os.path.abspath(csvpath)), fieldnames, skiprows=1),
                CountEmitter(every=1000),
                
                FieldRemover('id'),
                FieldRemover('import_reference'),
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
                
                MD5Filter(urn_with_name_fallback('contributor_urn', 'contributor_name'), 'contributor_entity'),
                MD5Filter(urn_with_name_fallback('recipient_urn', 'recipient_name'), 'recipient_entity'),
                MD5Filter(urn_with_name_fallback('committee_urn', 'committee_name'), 'committee_entity'),
                MD5Filter(urn_with_name_fallback('organization_urn', 'organization_name'), 'organization_entity'),
                MD5Filter(urn_with_name_fallback('parent_organization_urn', 'parent_organization_name'), 'parent_organization_entity'),
                
                #DebugEmitter(),
                AbortFilter(),
                LoaderEmitter(loader),
                
            )
        finally:
            sys.stdout.flush()
            sys.stderr.flush()
