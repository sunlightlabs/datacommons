
"""
Build the Entity table from the Contribution table. 

Transactions with identical organization_name belong to the same entity.
"""
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'


from dcdata.contribution.models import sql_names, Contribution
from matchbox_scripts.support.build_entities import populate_entities


def get_a_recipient_type(id):
    t = Contribution.objects.filter(recipient_entity=id)[0]
    if t.recipient_type == 'C':
        return 'committee'
    elif t.recipient_type == 'P':
        return 'politician'

def run():
    populate_entities(sql_names['contribution'], 
                      sql_names['contribution_organization_name'], 
                      sql_names['contribution_organization_entity'],
                      [sql_names['contribution_organization_name'], sql_names['contribution_contributor_employer']],
                      [sql_names['contribution_organization_urn']],
                      (lambda id: 'organization'))
    populate_entities(sql_names['contribution'],
                      sql_names['contribution_recipient_name'],
                      sql_names['contribution_recipient_entity'],
                      [sql_names['contribution_recipient_name']],
                      [sql_names['contribution_recipient_urn']],
                      get_a_recipient_type)
    populate_entities(sql_names['contribution'],
                      sql_names['contribution_committee_name'],
                      sql_names['contribution_committee_entity'],
                      [sql_names['contribution_committee_name']],
                      [sql_names['contribution_committee_urn']],
                      (lambda id: 'committee'))
    
    
if __name__ == '__main__':
    run()
    
    