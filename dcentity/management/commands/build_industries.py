import csv
import sys
import traceback

from django.db import transaction
from django.core.management.base import BaseCommand

from dcentity.entity import build_entity


@transaction.commit_on_success
def build_industries(csv_rows):
    industries_seen = {}
    for (source, code, name, industry, order) in csv.reader(csv_rows):
        try:
            industry = industry.strip()
            source = source.strip()
            order = order.strip()

            if industries_seen.has_key(industry) or industry == 'industry':
                continue
            else:
                industries_seen[industry] = 1

            print 'Generating entity for %s, %s, %s' % (source, industry, order)

            attributes = []
            if source == 'NIMSP':
                attributes.append(('urn:nimsp:industry', order))
            else:
                attributes.append(('urn:crp:industry', order))

            build_entity(industry, 'industry', attributes)

        except:
            traceback.print_exception(*sys.exc_info())
            print "!!!!! Skipping Entity: %s !!!!!" % name
        sys.stdout.flush()


class Command(BaseCommand):
    def handle(self, input_path, **args):
        build_industries(open(input_path, 'r'))


