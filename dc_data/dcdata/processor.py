import operator

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
        for output in record_processor(record):
            output_func(output)


def chain_filters(*filters):
    return compose_one2many(*map(lambda filter: lambda x: filter(None, [x]), filters))

def compose_one2many(*filters):
    def chain(record, remaining_filters):
        if not remaining_filters:
            return [record]
        return reduce(operator.add, [chain(result, remaining_filters[1:]) for result in remaining_filters[0](record)], [])
    
    return lambda r: chain(r, filters) 

    

# I've left this all in a messed-up state. The problem is that I build the whole framework on the assumption
# that process_record takes a single input and returns a single output. This isn't true for the SaltFilter,
# which returns a generator giving 1 or 2 records. So I'm trying to rewrite the main loop and the filter chain.
# Instead of using the Filter.process_record method (which is unusable because it could return one output or a
# generator), I'm using the Filter.__call__ method, which takes a recipe plus an iterator of inputs and returns
# a generator of outputs. 
#
# But I don't want to use this directly on the source--then we'd be back to saucebrush recipes, where we don't
# have a good way to do error handling, reporting, or separation of output.
#
# So I'm trying to make the chain_filters function map a list of filters to a function from one input to a list
# of outputs. And somewhere in there it's all getting confused and not working right.
#
# Just got the unit test using Filters passing. The unit test using regular funcitons is totally broken, because
# I forgot that the functions should take iterators as input, not a single input. Might just want to scrap that.
#
# CAREFUL: I'm concerned about passing around records that are modified by filters...could we get in a situation
# where the same object is returned more than once, and then a subsequent filter tries to modify one reference
# to that object and ends up inadvertently modifying the other reference as well?
#
# Once the chain_filters method is working, the load_data method will need to be rewritten, and then all the client
# code will need to call the chain_filters function instead of get_chained_filter.
#
# UPDATE: chain_filters is now working. See above two paragrphas for next steps.

