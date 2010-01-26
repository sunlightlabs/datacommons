
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

import sys
import traceback
import csv


from matchbox_scripts.support.build_entities import build_entity
from scripts.crp.denormalize import contributor_urn


def build_big_hitters(csv_rows):
    def parse(crp_id, nimsp_id, name):
        nimsp_urn = 'urn:nimsp:contributor:' + nimsp_id.strip()
        clean_name = name.strip().decode('utf8', 'replace')
        
        columns = ['contributor', 'organization', 'parent_organization', 'committee', 'recipient']
        name_columns = [column + '_name' for column in columns]
        urn_columns = [column + '_urn' for column in columns]
        entity_columns = [column + '_entity' for column in columns]
        
        name_criteria = zip(name_columns, [clean_name] * 5, entity_columns)
        nimsp_urn_criteria = zip(urn_columns[0:3], [nimsp_urn] * 3, entity_columns[0:3])
        
        all_criteria = name_criteria + nimsp_urn_criteria
        
        return (clean_name, 'organization', all_criteria)
    
    aggregate_stats = dict()
    entity_stats = dict()
    for row_values in csv.reader(csv_rows):
        print "Building entity for row '%s'" % row_values
        entity_stats.clear()
        try:
            (name, type, criteria) = parse(*row_values)
            build_entity(name, type, criteria, entity_stats)
            print "Stats: %s" % entity_stats
            aggregate_stats.update(entity_stats)
        except:
            traceback.print_exception(*sys.exc_info())
            print "!!!!! Skipping Entity: %s !!!!!" % row_values
        sys.stdout.flush()
            
    totals = dict()
    for ((column, value), count) in aggregate_stats.iteritems():
        if column.endswith("_name"):
            totals[column] = totals.get(column, 0) + count
        elif value.startswith("urn:crp"):
            totals[column + "_crp"] = totals.get(column + "_crp", 0) + count
        else:
            totals[column + "_nimsp"] = totals.get(column + "_nimsp", 0) + count

    print "Total usage statistics:\n %s" % totals


if __name__ == "__main__":
    build_big_hitters(open(sys.argv[1]))
    
    