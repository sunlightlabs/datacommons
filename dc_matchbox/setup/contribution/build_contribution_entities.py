
"""
Build the Entity table from the Contribution table. 

Transactions with identical organization_name belong to the same entity.
"""
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'


from dcdata.utils.sql import dict_union, is_disjoint
from dcdata.contribution.models import sql_names as contribution_names
from matchbox.models import sql_names as matchbox_names
assert is_disjoint(contribution_names, matchbox_names)
sql_names = dict_union(contribution_names, matchbox_names)    
    
from setup.support.build_entities import populate_entities
    
if __name__ == '__main__':
    populate_entities(sql_names['contribution'], 
                      sql_names['contribution_organization_name'], 
                      sql_names['contribution_organization_entity'])