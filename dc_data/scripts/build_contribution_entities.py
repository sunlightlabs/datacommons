
"""
Build the Entity table from the Contribution table. 

Transactions with identical organization_name belong to the same entity.
"""

import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

import MySQLdb
from settings import DATABASE_NAME, DATABASE_USER, DATABASE_HOST
from sql_utils import dict_union, is_disjoint
from dcdata.contribution.models import sql_names as contribution_names
from matchbox.models import sql_names as matchbox_names
assert is_disjoint(contribution_names, matchbox_names)
sql_names = dict_union(contribution_names, matchbox_names)    
    
from build_entities import populate_entities
    
if __name__ == '__main__':

    
    connection = MySQLdb.connect(host=DATABASE_HOST, user=DATABASE_USER, db=DATABASE_NAME)
    populate_entities(connection, 
                      sql_names['contribution'], 
                      sql_names['contribution_organization_name'], 
                      sql_names['contribution_organization_entity'])