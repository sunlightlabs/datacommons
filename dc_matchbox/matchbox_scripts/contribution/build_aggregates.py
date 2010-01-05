
from django.db import connection, transaction


def build_aggregates():
    cursor = connection.cursor()
    
    cursor.execute("drop table if exists matchbox_contribution_aggregates")
    
    cursor.execute("""
                    create table matchbox_contribution_aggregates as
                    select e.id, count(distinct c.id), sum(c.amount)
                    from matchbox_entity e left join contribution_contribution c on
                        e.id = c.contributor_entity or  
                        e.id = c.organization_entity or
                        e.id = c.parent_organization_entity or
                        e.id = c.committee_entity or
                        e.id = c.recipient_entity
                    group by e.id """)

    cursor.execute("create index matchbox_contribution_aggregates_id on matchbox_contribution_aggregates (id)")
    
    
if __name__ == '__main__':
    build_aggregates()