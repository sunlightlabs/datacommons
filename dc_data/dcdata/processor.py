from saucebrush.filters import Filter
from django.core.management.base import BaseCommand



# A Data Commons data loader should be a Django Command object obeying the following interface:
#    1) the command should be runnable at the command line through 'python manage.py <command-name>'
#      or programmatically through 'call_command'. This is accomplished in Django by putting the
#      class in the management.commands.<command-name> package under the variable name 'Command'.
#      The main functionality of the command goes in the 'handle' method. The 'handle' method should
#      prepare the input iterator, processor function, and output function, and pass them on to
#      the 'load_data' function.
#    2) the command should provide a static 'get_record_processor' function, which returns a function
#      mapping an input record to an output. 'get_record_processor' can take as a parameter whatever
#      context is necessary for processing individual records. For example, for CRP denormalization
#      this means catcodes, candidates, and committees. 
#
# Point 1) ensures a somewhat consistent interface for running commands. Point 2) ensures that unit
# tests can be easily written against a command. And finally, using the 'load_data' function as
# the basis for the 'handle' method ensures consistent error handling and reporting across commands.



# this method looks a little bare right now, but error handling and reporting will be going in soon
def load_data(input_iterator, record_processor, output_func):
    
    for record in input_iterator:
        output = record_processor(record)
        output_func(output)
            
            

            
class ChainedFilter(Filter):
    def __init__(self, *filters):
        self.filters = filters
    
    def process_record(self, record):
        for filter in self.filters:
            record = filter.process_record(record)
            
        return record
    
    
def get_chained_processor(*filters):
    return ChainedFilter(*filters).process_record