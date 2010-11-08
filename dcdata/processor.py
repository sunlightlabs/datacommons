import operator
import sys
import traceback
from datetime import datetime



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



# might want to set the to True during debugging.
TERMINATE_ON_ERROR = False


# this method looks a little bare right now, but error handling and reporting will be going in soon
def load_data(input_iterator, record_processor, output_func):
    
    for record in input_iterator:
        try:
            
            for output in record_processor(record):
                output_func(output)
                
        except SkipRecordException as e:
            sys.stderr.write('Skipping processing of input record: "%s"\n' % record)
            sys.stderr.write('Exception: %s', e)
            if e.traceback:
                traceback.print_tb(e.traceback)
            sys.stderr.flush()
            if TERMINATE_ON_ERROR:
                raise
            
        except TerminateProcessingException as e:
            sys.stderr.write('Terminating processing on input record: "%s"\n' % record)
            raise



class Every(object):
    def __init__(self, n, func):
        self.i = 0
        self.n = n
        self.func = func
        
    def __call__(self, ignored, records):
        self.i += 1
        if self.i % self.n == 0:
            self.func(self.i)
        
        return records


def progress_tick(i):
    sys.stdout.write("%s: Output %d records.\n" % (datetime.now(), i))
    sys.stdout.flush()
    

def chain_filters(*filters):
    return compose_one2many(*map(lambda filter: lambda x: filter(None, [x]), filters))


def compose_one2many(*filters):
    def chain(record, remaining_filters):
        if not remaining_filters:
            return [record]
        return reduce(operator.add, [chain(result, remaining_filters[1:]) for result in remaining_filters[0](record)], [])
    
    return lambda r: chain(r, filters) 


class SkipRecordException(Exception):
    """ An exception that tells the data loader to skip all output records from the current input record. """
    
    def __init__(self, message, traceback=None):    
        super(SkipRecordException, self).__init__(message)
        self.traceback = traceback
    
class TerminateProcessingException(Exception):
    """ An exception that tells the data loader to skip all output records from the current input record. """
    
    def __init__(self, message, traceback=None):    
        super(TerminateProcessingException, self).__init__(message)
        self.traceback = traceback    

