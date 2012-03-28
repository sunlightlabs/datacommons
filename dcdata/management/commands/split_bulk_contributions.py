
from dcapi.contributions.handlers import CONTRIBUTION_FIELDS
from dcdata.contribution.models import Contribution
from dcdata.loading import model_fields
from dcdata.management.commands.crp_denormalize import SpecFilter
from dcdata.processor import chain_filters, load_data
from django.core.management.base import BaseCommand
from optparse import make_option
from saucebrush.emitters import Emitter, CSVEmitter
from saucebrush.filters import FieldRemover
from saucebrush.sources import CSVSource
import os


class ConditionalEmitter(Emitter):
    
    def __init__(self, condition, emitter):
        self.condition = condition
        self.emitter = emitter
        
    def emit_record(self, record):
        if self.condition(record):
            self.emitter.emit_record(record)

def check_namespace(namespace_substring):
    return lambda r: namespace_substring in r['transaction_namespace']

def check_namespace_and_cycle(namespace_substring, cycle):
    return lambda r: namespace_substring in r['transaction_namespace'] and r['cycle'] in (str(cycle), str(cycle - 1))
    

class SplitBulkContributionsCommand(BaseCommand):
    
    help = "Split a CSV dump of the contribution table into files broken down by state and cycle."
    
    option_list = BaseCommand.option_list + (
        make_option('--output', '-o', dest='out_dir', default='split',
            help='Output directory'),
    )
        
    def handle(self, input_path, **options):
        
        output_dir = options['out_dir']
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)
        
        input_fields = model_fields('contribution.Contribution')
        source = CSVSource(open(input_path, 'r'), input_fields)
        
        outputs = []
        
        outputs.append(CSVEmitter(open(os.path.join(output_dir, 'contributions.all.csv'), 'w'), CONTRIBUTION_FIELDS))
        
        for namespace in ('fec', 'nimsp'):
            namespace_condition = check_namespace(namespace)
            out_file = open(os.path.join(output_dir, 'contributions.%s.csv' % namespace), 'w')
            emitter = ConditionalEmitter(namespace_condition, CSVEmitter(out_file, CONTRIBUTION_FIELDS))
            outputs.append(emitter)
            
            for cycle in range(1990, 2012, 2):
                cycle_condition = check_namespace_and_cycle(namespace, cycle)
                out_file = open(os.path.join(output_dir, 'contributions.%s.%s.csv' % (namespace, cycle)), 'w')
                emitter = ConditionalEmitter(cycle_condition, CSVEmitter(out_file, CONTRIBUTION_FIELDS))
                outputs.append(emitter)
                
        processor = chain_filters(FieldRemover(['id', 'import_reference']))
        
           
        combined_output = chain_filters(*outputs)
                
        load_data(source, processor, combined_output)
        
        
Command = SplitBulkContributionsCommand       

