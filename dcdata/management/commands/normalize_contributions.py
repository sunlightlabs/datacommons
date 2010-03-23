
import os
from django.core.management.base import BaseCommand
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

import traceback
import sys
import csv

from django.db import connection, transaction

from dcdata.utils.strings.normalizer import basic_normalizer


def normalize_file(originals, out):
    csv_out = csv.writer(out)
    for original in originals:
        original = original.rstrip('\n').decode('utf8', 'replace')
        normalized = basic_normalizer(original)
        if normalized:
            csv_out.writerow([original, normalized])
    
    
def download_names(out):
    cursor = connection.cursor()
    
    cursor.execute('drop table if exists tmp_all_names')
    
    stmt = """
            create table tmp_all_names as
                select distinct contributor_name from contribution_contribution where contributor_name != ''
                union select distinct contributor_employer from contribution_contribution where contributor_employer != ''
                union select distinct organization_name from contribution_contribution where organization_name != ''
                union select distinct parent_organization_name from contribution_contribution where parent_organization_name != ''
                union select distinct committee_name from contribution_contribution where committee_name != ''
                union select distinct recipient_name from contribution_contribution where recipient_name != '';
           """
    cursor.execute(stmt)
    
    cursor.copy_to(out, 'tmp_all_names')
    
    cursor.execute('drop table if exists tmp_all_names')

    
@transaction.commit_on_success
def upload_normalizations(normalizations):
    transaction.set_dirty()

    cursor = connection.cursor()

    cursor.execute("delete from matchbox_normalization")
    
    try:
        cursor.copy_from(normalizations, 'matchbox_normalization', sep=',')
    except:
        traceback.print_exception(*sys.exc_info())
        raise
    
    
def normalize_contributions():

    originals_filename = '/tmp/originals.out'
    normalized_filename = '/tmp/normalized.csv'
    
    originals_writer = open(originals_filename, 'w')
    download_names(originals_writer)
    originals_writer.close()
    
    originals_reader = open(originals_filename, 'r')
    normalized_writer = open(normalized_filename, 'w')
    normalize_file(originals_reader, normalized_writer)
    normalized_writer.close()
    
    normalized_reader = open(normalized_filename, 'r')
    upload_normalizations(normalized_reader)

    print "Normalization successful..."


class Command(BaseCommand):
    def handle(self, **args):
        normalize_contributions()

