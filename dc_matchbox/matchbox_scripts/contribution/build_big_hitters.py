
import os
from dcdata.contribution.models import NIMSP_TRANSACTION_NAMESPACE
from matchbox.queries import recompute_aggregates
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

import sys
import traceback
import csv

from django.db import transaction, connection

from matchbox.models import *



@transaction.commit_on_success
def build_entity(name, type, crp_id, nimsp_id):
    
    def _execute(stmt, args):     
        try:
            cursor.execute(stmt, args)
        except:
            print "build_entity(): Error executing query: '%s' %% (%s)" % (stmt, args)
            raise
        
    cursor = connection.cursor()
    
    e = Entity.objects.create(name=name, type=type)
    
    # to do: build EntityAttribute entries
    
    # match records based on NIMSP ID
    for column in ['contributor', 'organization', 'parent_organization']:
        stmt = """
           update contribution_contribution set %s = %%s
           where
               transaction_namespace = %%s
               and %s = %%s
           """ % (column + '_entity', column + '_ext_id')                
        _execute(stmt, [e.id, NIMSP_TRANSACTION_NAMESPACE, nimsp_id])

    # match records based on normalized name
    normalized_name = basic_normalizer(name)
    for column in ['contributor', 'organization', 'parent_organization', 'committee', 'recipient']:
        stmt = """
           update contribution_contribution set %s = %%s
           from matchbox_normalization  
           where 
               matchbox_normalization.original = contribution_contribution.%s 
               and matchbox_normalization.normalized = %%s
           """ % (column + '_entity',  column + '_name')
        _execute(stmt, [e.id, normalized_name])
        
    EntityAlias.objects.create(entity=e, alias=name, verified=True)
    EntityAttribute.objects.create(entity=e, namespace=EntityAttribute.ENTITY_ID_NAMESPACE, value = e.id, verified=True)
    EntityAttribute.objects.create(entity=e, namespace='urn:crp:organization', value=crp_id, verified=True)
    EntityAttribute.objects.create(entity=e, namespace='urn:nimsp:organization', value=nimsp_id, verified=True)    
    
    recompute_aggregates(e.id)
        



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
    
    