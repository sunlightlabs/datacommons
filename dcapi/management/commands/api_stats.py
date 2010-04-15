from dcapi.models import Invocation
from django.core.management.base import BaseCommand
from datetime import datetime, timedelta




def print_stats(execution_times):
    print "Number of calls: %s\tMean execution time: %s" % (len(execution_times), float(sum(execution_times)) / len(execution_times))
    
    for percentile in [0, 5, 25, 50, 75, 95, 99]:
        print "%s\t|\t%s" % (percentile, execution_times[len(execution_times) * percentile / 100])
  

class ShowAPIStats(BaseCommand):
    
    def handle(self, *args, **options):

        invocations = Invocation.objects.using('production').filter(timestamp__gt=datetime.utcnow() - timedelta(days=1)).order_by('execution_time')
        
        print "API Statistics for the last 24 hours:"
        
        print "--- All CALLS ---"
        print_stats([i.execution_time for i in invocations])
        print 

        print "--- SMALL RESULT SETS ---"
        print_stats([i.execution_time for i in invocations if i.total_records <= 100])
        print
        
        print "--- FULL-TEXT SEARCHES ---"
        print_stats([i.execution_time for i in invocations if '_ft' in i.query_string])
        print
        
        print "--- NON-FULL-TEXT SEARCHES ---"
        print_stats([i.execution_time for i in invocations if '_ft' not in i.query_string])
  
          
Command = ShowAPIStats