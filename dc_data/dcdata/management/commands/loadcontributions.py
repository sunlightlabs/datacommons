# -*- coding: utf-8 -*-


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
from optparse import make_option
import os
import sys
import traceback


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
                    sys.stderr.flush()
                raise Exception('Abort: %s of %s records contained errors' % (reject_count, self._record_count))
        return record
    
    
class UnicodeFilter(Filter):
    def __init__(self, method='replace'):
        self._method = method
        
    def process_record(self, record):
        for (key, value) in record.items():
            if isinstance(value, str):
                # decoding and encoding seem weird...
                # but in testing I tried decoding the '�' character ('\xc2\xbb')
                # and it gave u'\xbb', which is NOT valid unicode. Running encode
                # gave back the original string '\xc2\xbb', which is the correct encoding.
                # I don't fully understand it, but from the output of '\xc2\xbb'.decode('utf8')
                # I can only conclude that there's a bug in Python's unicode handling...
                # or that I'm misunderstanding something.
                record[key] = value.decode('utf8', self._method).encode('utf8')
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

    option_list = BaseCommand.option_list + (
        make_option('--source', '-s', dest='source', default='CRP', metavar="(CRP|NIMSP)",
            help='Data source'),
    )
    
    @transaction.commit_on_success
    def handle(self, csvpath, *args, **options):
        
        fieldnames = model_fields('contribution.Contribution')
        
        loader = ContributionLoader(
            source=options.get('source'),
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
                ISODateFilter('date'),
                BooleanFilter('is_amendment'),
                FloatFilter('amount'),
                UnicodeFilter(),
                
                ContributorFilter(),
                OrganizationFilter(),
                ParentOrganizationFilter(),
                RecipientFilter(),
                CommitteeFilter(),
                
                #DebugEmitter(),
                AbortFilter(0.001), # fail if over 1 in 1000 records is bad
                LoaderEmitter(loader),
                
            )
        except:
            traceback.print_exception(*sys.exc_info())
            raise
        finally:
            sys.stdout.flush()
            sys.stderr.flush()
