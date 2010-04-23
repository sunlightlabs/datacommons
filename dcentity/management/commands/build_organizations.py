

import csv
import sys
import traceback

from django.db import transaction
from django.core.management.base import BaseCommand

from dcentity.entity import build_entity



@transaction.commit_on_success
def build_organizations(csv_rows):
    for (crp_id, nimsp_id, name) in csv.reader(csv_rows):
        try:
            name = name.strip().decode('utf8', 'replace')
            crp_id = crp_id.strip()
            nimsp_id = nimsp_id.strip()
            
            attributes = []
            if nimsp_id:
                attributes.append(('urn:nimsp:organization', nimsp_id))
            if crp_id:
                attributes.append(('urn:crp:organization', crp_id))
            
            build_entity(name, 'organization', attributes)
            
        except:
            traceback.print_exception(*sys.exc_info())
            print "!!!!! Skipping Entity: %s !!!!!" % name
        sys.stdout.flush()
            

class Command(BaseCommand):
    def handle(self, input_path, **args):
        build_organizations(open(input_path, 'r'))
    
    