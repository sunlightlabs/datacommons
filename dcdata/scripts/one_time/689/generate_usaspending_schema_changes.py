import csv, os.path
from datatypes import datatypes

datasets = [
    ('fields_unified_fpds.csv', 'fpds_changes.sql', 'contracts_contract'),
    ('fields_unified_faads.csv', 'faads_changes.sql', 'grants_grant'),
]

def generate_sql(reader, output_file, table):
    for line in reader:
        orig, kevins, ours = line

        if kevins and ours:
            print >> output_file, 'alter table {0} alter column {1} rename to {2};'.format(table, ours, kevins)
        elif kevins:
            datatype = datatypes['fpds'].get(kevins) or datatypes['fpds'].get(orig) or 'BLIMEY!!!'
            print >> output_file, 'alter table {0} add column {1} {2};'.format(table, kevins, datatype)
        elif ours and orig:
            print >> output_file, 'alter table {0} alter column {1} rename to {2};'.format(table, ours, orig.lower())


for set in datasets:
    field_guide, output_filename, table = set
    reader = csv.reader(open(os.path.abspath(field_guide), 'r'))
    output_file = open(os.path.abspath(output_filename), 'w')

    generate_sql(reader, output_file, table)

