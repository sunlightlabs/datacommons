
"""
Build the Entity table from the Contribution table. 

Transactions with identical organization_name belong to the same entity.
"""
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'


from dcdata.contribution.models import sql_names, Contribution


def get_a_recipient_type(cursor, id):
    """
    Return either 'committee' or 'politician' based on the recipient_type of an arbitrary transaction with the given id.
    """
    
    t = Contribution.objects.filter(recipient_entity=id)[:1][0]
    if t.recipient_type == 'C':
        return 'committee'
    elif t.recipient_type == 'P':
        return 'politician'

def get_a_contributor_type(cursor, id):
    stmt = "select %s from %s where %s = %%s limit 1" % (sql_names['contribution_contributor_type'], sql_names['contribution'], sql_names['contribution_contributor_entity'])
    cursor.execute(stmt, [id])
    if cursor.rowcount and cursor.fetchone()[0] == 'C':
            return 'committee'    
    return 'individual'
    
    

def run():
    
    log("Building contributor entities...")
    populate_entities(sql_names['contribution'],
                      sql_names['contribution_contributor_name'],
                      sql_names['contribution_contributor_entity'],
                      [sql_names['contribution_contributor_name']],
                      [sql_names['contribution_contributor_urn']],
                       get_a_contributor_type)
    
    log("Building organization entities...")
    populate_entities(sql_names['contribution'], 
                      sql_names['contribution_organization_name'], 
                      sql_names['contribution_organization_entity'],
                      [sql_names['contribution_organization_name'], sql_names['contribution_contributor_employer']],
                      [sql_names['contribution_organization_urn']],
                      (lambda cursor, id: 'organization'))   
     
    log("Building parent organization entities...")
    populate_entities(sql_names['contribution'], 
                      sql_names['contribution_parent_organization_name'], 
                      sql_names['contribution_parent_organization_entity'],
                      [sql_names['contribution_parent_organization_name']],
                      [sql_names['contribution_parent_organization_urn']],
                      (lambda cursor, id: 'organization'))
    
    log("Building recipient entities...")
    populate_entities(sql_names['contribution'],
                      sql_names['contribution_recipient_name'],
                      sql_names['contribution_recipient_entity'],
                      [sql_names['contribution_recipient_name']],
                      [sql_names['contribution_recipient_urn']],
                      get_a_recipient_type)
    
    log("Building committee entities...")
    populate_entities(sql_names['contribution'],
                      sql_names['contribution_committee_name'],
                      sql_names['contribution_committee_entity'],
                      [sql_names['contribution_committee_name']],
                      [sql_names['contribution_committee_urn']],
                      (lambda cursor, id: 'committee'))
    
    
from matchbox_scripts.support.build_entities import populate_entities
from matchbox_scripts.build_matchbox import log

    
if __name__ == '__main__':
    run()
    
    