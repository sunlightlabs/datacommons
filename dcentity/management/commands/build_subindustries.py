import csv
import sys
import traceback

from django.db import transaction
from django.core.management.base import BaseCommand

from dcentity.entity import build_entity


@transaction.commit_on_success
def build_subindustries(csv_rows):
    for (source, code, name, industry, order) in csv.reader(csv_rows):
        try:
            code = code.strip()
            name = name.strip()
            source = source.strip()

            print 'Generating entity for %s, %s, %s' % (source, code, name)

            attributes = []
            if source == 'NIMSP':
                attributes.append(('urn:nimsp:subindustry', code))
            else:
                attributes.append(('urn:crp:subindustry', code))

            build_entity(name, 'industry', attributes)

        except:
            traceback.print_exception(*sys.exc_info())
            print "!!!!! Skipping Entity: %s !!!!!" % name
        sys.stdout.flush()


class Command(BaseCommand):
    def handle(self, input_path, **args):
        build_subindustries(open(input_path, 'r'))


