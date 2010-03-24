
import os

from django.core.management.base import BaseCommand
from matchbox.entity import build_org_entity, build_recipient_entity
from dcdata.contribution.models import CRP_TRANSACTION_NAMESPACE
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

import sys
import traceback
import csv



def build_big_hitters(csv_rows):
    #for (crp_id, nimsp_id, name) in csv.reader(csv_rows):
    for (name,id) in csv.reader(csv_rows):
        try:
            clean_name = name.strip().decode('utf8', 'replace')
            #build_org_entity(clean_name, crp_id.strip(), nimsp_id.strip())
            build_recipient_entity(clean_name, CRP_TRANSACTION_NAMESPACE, id)
        except:
            traceback.print_exception(*sys.exc_info())
            print "!!!!! Skipping Entity: %s !!!!!" % name
        sys.stdout.flush()
            

class Command(BaseCommand):
    def handle(self, input_path, **args):
        build_big_hitters(open(input_path, 'r'))
    
    