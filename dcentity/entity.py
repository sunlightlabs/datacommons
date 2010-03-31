

from dcdata.contribution.models import NIMSP_TRANSACTION_NAMESPACE,\
    CRP_TRANSACTION_NAMESPACE
from dcentity.queries import recompute_aggregates


from django.db import transaction, connection

from dcentity.models import *


#@transaction.commit_on_success
def build_recipient_entity(name, namespace, id):
    cursor = connection.cursor()
    
    e = Entity.objects.create(name=name, type='politician')

    EntityAlias.objects.create(entity=e, alias=name, verified=True)
    EntityAttribute.objects.create(entity=e, namespace=EntityAttribute.ENTITY_ID_NAMESPACE, value = e.id, verified=True)
    if namespace == NIMSP_TRANSACTION_NAMESPACE:
        attr_namespace = 'urn:nimsp:recipient'
    elif namespace == CRP_TRANSACTION_NAMESPACE:
        attr_namespace = 'urn:crp:recipient'
    if id:
        EntityAttribute.objects.create(entity=e, namespace=attr_namespace, value=id, verified=True)
    



@transaction.commit_on_success
def build_org_entity(name, crp_id, nimsp_id):
    cursor = connection.cursor()
    
    e = Entity.objects.create(name=name, type='organization')
        
    EntityAlias.objects.create(entity=e, alias=name, verified=True)
    EntityAttribute.objects.create(entity=e, namespace=EntityAttribute.ENTITY_ID_NAMESPACE, value = e.id, verified=True)
    if crp_id:
        EntityAttribute.objects.create(entity=e, namespace='urn:crp:organization', value=crp_id, verified=True)
    if nimsp_id:
        EntityAttribute.objects.create(entity=e, namespace='urn:nimsp:organization', value=nimsp_id, verified=True)    
    
        

def _execute(cursor, stmt, args):     
    try:
        cursor.execute(stmt, args)
    except:
        print "build_entity(): Error executing query: '%s' %% (%s)" % (stmt, args)
        raise
    
def _associate_ids(cursor, entity_id, namespace, ext_id, column_prefixes):
    for column in column_prefixes:
        stmt = """
           update contribution_contribution set %s = %%s
           where
               transaction_namespace = %%s
               and %s = %%s
           """ % (column + '_entity', column + '_ext_id')                
        _execute(cursor, stmt, [entity_id, namespace, ext_id])    
        
def _associate_names(cursor, entity_id, name, column_prefixes):
    normalized_name = basic_normalizer(name)
    for column in column_prefixes:
        stmt = """
           update contribution_contribution set %s = %%s
           from matchbox_normalization  
           where 
               matchbox_normalization.original = contribution_contribution.%s 
               and matchbox_normalization.normalized = %%s
           """ % (column + '_entity',  column + '_name')
        _execute(cursor, stmt, [entity_id, normalized_name])
    
