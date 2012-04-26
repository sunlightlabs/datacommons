import csv
import sys
import traceback

from django.db import transaction
from django.core.management.base import BaseCommand

from dcentity.entity import build_entity


@transaction.commit_on_success
def build_committees(csv_rows):
    for (fec_id, name) in csv.reader(csv_rows):
        try:
            print 'Generating entity for %s, %s' % (fec_id, name)

            name = name.strip().decode('utf8', 'replace')
            fec_id = fec_id.strip()

            attributes = []
            attributes.append(('urn:fec:committee', fec_id))

            build_entity(name, 'organization', attributes)

        except:
            traceback.print_exception(*sys.exc_info())
            print "!!!!! Skipping Entity: %s !!!!!" % name
        sys.stdout.flush()


class Command(BaseCommand):
    def handle(self, input_path, **args):
        build_committees(open(input_path, 'r'))


