
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

import sys
import traceback
import csv


from matchbox_scripts.support.build_entities import build_entity


def build_big_hitters(csv_rows):
    for (crp_id, nimsp_id, name) in csv.reader(csv_rows):
        try:
            clean_name = name.strip().decode('utf8', 'replace')
            build_entity(clean_name, 'organization', crp_id.strip(), nimsp_id.strip())
        except:
            traceback.print_exception(*sys.exc_info())
            print "!!!!! Skipping Entity: %s !!!!!" % name
        sys.stdout.flush()
            

if __name__ == "__main__":
    build_big_hitters(open(sys.argv[1], 'r'))
    
    