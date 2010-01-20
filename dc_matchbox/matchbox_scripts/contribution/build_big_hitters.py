
import sys
import csv

from matchbox_scripts.support.build_entities import build_entity
from scripts.crp.denormalize import contributor_urn


def build_big_hitters(csv_rows):
    def parse(crp_id, nimsp_id, name):
        crp_urn = contributor_urn(crp_id.strip())
        nimsp_urn = 'urn:nimsp:contributor:' + nimsp_id.strip()
        clean_name = name.strip()
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
    build_big_hitters(sys.argv[1])