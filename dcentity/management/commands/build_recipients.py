
import os

from django.core.management.base import BaseCommand
from dcentity.entity import build_org_entity, build_recipient_entity
from dcdata.contribution.models import CRP_TRANSACTION_NAMESPACE
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

import sys
import traceback
import csv



def build_recipients(csv_rows):
    for (name,id,namespace) in csv.reader(csv_rows):
        try:
            print 'Generating entity for %s, %s, %s' % (name, namespace, id)
            clean_name = name.strip().decode('utf8', 'replace')
            build_recipient_entity(clean_name, namespace, id)
        except:
            traceback.print_exception(*sys.exc_info())
            print "!!!!! Skipping Entity: %s !!!!!" % name
        finally:
            sys.stderr.flush()
            sys.stdout.flush()
            

class Command(BaseCommand):
    def handle(self, input_path, **args):
        build_recipients(open(input_path, 'r'))
    
    