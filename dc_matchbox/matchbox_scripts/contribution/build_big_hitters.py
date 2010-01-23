
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

import sys
import csv

from django.db import transaction

from matchbox_scripts.support.build_entities import build_entity
from scripts.crp.denormalize import contributor_urn


@transaction.commit_on_success
def build_big_hitters(csv_rows):
    def parse(crp_id, nimsp_id, name):
        crp_urn = contributor_urn(crp_id.strip())
        nimsp_urn = 'urn:nimsp:contributor:' + nimsp_id.strip()
        clean_name = name.strip().decode('utf8', 'replace')
        
        columns = ['contributor', 'organization', 'parent_organization', 'committee', 'recipient']
        name_columns = [column + '_name' for column in columns]
        urn_columns = [column + '_urn' for column in columns]
        entity_columns = [column + '_entity' for column in columns]
        
        name_criteria = zip(name_columns, [clean_name] * 5, entity_columns)
        crp_urn_criteria = zip(urn_columns, [crp_urn] * 5, entity_columns)
        nimsp_urn_criteria = zip(urn_columns, [nimsp_urn] * 5, entity_columns)
        
        return (clean_name, 'organization', name_criteria + crp_urn_criteria + nimsp_urn_criteria)
    
    for row_values in csv.reader(csv_rows):
        print "Building entity for row '%s'" % row_values
        build_entity(*parse(*row_values))
        
        


if __name__ == "__main__":
    build_big_hitters(open(sys.argv[1]))