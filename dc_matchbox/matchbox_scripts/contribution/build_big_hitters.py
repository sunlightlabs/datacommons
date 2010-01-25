
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
        return (clean_name, 'organization', [('contributor_name', clean_name, 'contributor_entity'),
                                       ('organization_name', clean_name, 'organization_entity'),
                                       ('parent_organization_name', clean_name, 'parent_organization_entity'),
                                       ('contributor_urn', nimsp_urn, 'contributor_entity'),
                                       ('organization_urn', nimsp_urn, 'organization_entity'),
                                       ('parent_organization_urn', nimsp_urn, 'parent_organization_entity'),
                                       ('contributor_urn', crp_urn, 'contributor_entity')])
        
    for row_values in csv.reader(csv_rows):
        build_entity(*parse(*row_values))


if __name__ == "__main__":
    build_big_hitters(open(sys.argv[1]))