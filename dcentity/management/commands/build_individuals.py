
import csv
import sys
import traceback

from django.db import transaction
from django.core.management.base import BaseCommand

from dcentity.entity import build_entity


@transaction.commit_on_success
def build_individuals(csv_rows):
    for (name,crp_id) in csv.reader(csv_rows):
        try:
            print 'Generating entity for %s, %s' % (name, crp_id)
            clean_name = name.strip().decode('utf8', 'replace')
            
            build_entity(clean_name, 'individual', [('urn:crp:individual', crp_id)])
            
        except:
            traceback.print_exception(*sys.exc_info())
            print "!!!!! Skipping Entity: %s !!!!!" % name
        finally:
            sys.stderr.flush()
            sys.stdout.flush()
            

class Command(BaseCommand):
    def handle(self, input_path, **args):
        build_individuals(open(input_path, 'r'))
    
    