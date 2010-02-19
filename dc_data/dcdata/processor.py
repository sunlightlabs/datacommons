from saucebrush.filters import Filter




class DataProcessor(object):
    
    @staticmethod
    def execute(self, command):
        raise NotImplementedError

    def process_record(self, record):
        raise NotImplementedError
    
    def process(self, input_iterator, output_func):
        
        for record in input_iterator:
            output = self.process_record(record)
            output_func(output)
            
            
            


            
class ChainedFilter(Filter):
    def __init__(self, *filters):
        self.filters = filters
    
    def process_record(self, record):
        for filter in self.filters:
            record = filter.process_record(record)
            
        return record