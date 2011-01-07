#!/usr/bin/env python

import csv, os.path
from datatypes import datatypes

datasets = [
    ('fields_unified_fpds.csv', 'fpds_changes.sql', 'contracts_contract', 'fpds'),
    ('fields_unified_faads.csv', 'faads_changes.sql', 'grants_grant', 'faads'),
]

def generate_sql(reader, output_file, table, datatype_key):
    for line in reader:
        if reader.line_num == 1: continue

        orig, kevins, ours = line

        if kevins and ours != '' and kevins.lower() != ours.lower():
            print >> output_file, 'alter table {0} rename {1} to {2};'.format(table, ours, kevins)
        elif kevins and ours == '':
            datatype = datatypes[datatype_key].get(kevins) or datatypes[datatype_key].get(orig) or 'BLIMEY!!!'
            print >> output_file, 'alter table {0} add column {1} {2};'.format(table, kevins, datatype)
        elif ours != '' and orig and (ours.lower() != orig.lower()):
            print >> output_file, 'alter table {0} rename {1} to {2};'.format(table, ours, orig.lower())


for set in datasets:
    field_guide, output_filename, table, datatype_key = set
    reader = csv.reader(open(os.path.abspath(field_guide), 'r'))
    output_file = open(os.path.abspath(output_filename), 'w')

    generate_sql(reader, output_file, table, datatype_key)

