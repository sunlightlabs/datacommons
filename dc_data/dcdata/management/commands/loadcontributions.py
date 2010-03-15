# -*- coding: utf-8 -*-


from dcdata.contribution.models import Contribution
from dcdata.loading import Loader, LoaderEmitter, model_fields, BooleanFilter, \
    EntityFilter
from dcdata.processor import chain_filters, load_data
from dcdata.utils.dryrub import CountEmitter, MD5Filter, CSVFieldVerifier,\
    VerifiedCSVSource
from decimal import Decimal
from django.core.exceptions import ImproperlyConfigured
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from optparse import make_option
from saucebrush.emitters import DebugEmitter
from saucebrush.filters import FieldRemover, FieldAdder, Filter, FieldModifier
from strings.normalizer import basic_normalizer
import os
import saucebrush
import sys
import traceback
from dcdata.utils.sql import parse_int, parse_date



# todo: we should just change the denormalize scripts to put the proper value in these fields
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

# todo: we should just change the denormalize scripts to put the proper value in these fields
class RecipientFilter(Filter):
    type_mapping = {'politician': 'P', 'committee': 'C'}
    def process_record(self, record):
        record['recipient_type'] = self.type_mapping.get(record['recipient_type'], None)
        return record

class CommitteeFilter(Filter):    
    def process_record(self, record):
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
        

class LoadContributions(BaseCommand):

    help = "load contributions from csv"
    args = ""

    requires_model_validation = False

    option_list = BaseCommand.option_list + (
        make_option('--source', '-s', dest='source', default='CRP', metavar="(CRP|NIMSP)",
            help='Data source'),
    )
    
    @staticmethod
    def get_record_processor(import_session):
        return chain_filters(
                CSVFieldVerifier(),
                
                FieldRemover('id'),
                FieldRemover('import_reference'),
                FieldAdder('import_reference', import_session),
                
                FieldModifier('amount', lambda a: Decimal(str(a))),
                FieldModifier(['cycle'], parse_int),
                FieldModifier(['date'], parse_date),
                BooleanFilter('is_amendment'),
                UnicodeFilter(),
                
                ContributorFilter(),
                OrganizationFilter(),
                ParentOrganizationFilter(),
                RecipientFilter(),
                CommitteeFilter())
    
    @transaction.commit_on_success
    def handle(self, csvpath, *args, **options):
        
        fieldnames = model_fields('contribution.Contribution')
        
        loader = ContributionLoader(
            source=options.get('source'),
            description='load from denormalized CSVs',
            imported_by="loadcontributions.py (%s)" % os.getenv('LOGNAME', 'unknown'),
        )
        
        try:
            input_iterator = VerifiedCSVSource(open(os.path.abspath(csvpath)), fieldnames, skiprows=1)
            output_func = LoaderEmitter(loader).process_record
            record_processor = self.get_record_processor(loader.import_session)

            load_data(input_iterator, record_processor, output_func)

        except:
            traceback.print_exception(*sys.exc_info())
            raise
        finally:
            sys.stdout.flush()
            sys.stderr.flush()
 
            
Command = LoadContributions
