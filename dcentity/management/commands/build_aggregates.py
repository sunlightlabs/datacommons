from django.core.management.base import BaseCommand

from django.db import connection, transaction


aggregate_count_stmt = """
    update matchbox_entity set contribution_count = (
        select count(*) from contribution_contribution 
        where contributor_entity = matchbox_entity.id
            or organization_entity = matchbox_entity.id
            or parent_organization_entity = matchbox_entity.id
            or committee_entity = matchbox_entity.id
            or recipient_entity = matchbox_entity.id
    )
"""


aggregate_amount_given_stmt = """
    update matchbox_entity set contribution_total_given = (
        select coalesce(sum(amount),0) from contribution_contribution
        where contributor_entity = matchbox_entity.id
            or organization_entity = matchbox_entity.id
            or parent_organization_entity = matchbox_entity.id
    )
"""

aggregate_amount_received_stmt = """
    update matchbox_entity set contribution_total_received = (
        select coalesce(sum(amount),0) from contribution_contribution
        where 
            committee_entity = matchbox_entity.id
            or recipient_entity = matchbox_entity.id
    )
"""

build_aliases_stmt = """
    insert into matchbox_entityalias (entity_id, alias, verified)
        select contributor_entity, contributor_name, FALSE
        from contribution_contribution
        where contributor_entity != ''
            and contributor_name != ''
        group by contributor_entity, contributor_name
    union
        select organization_entity, organization_name, FALSE
        from contribution_contribution
        where organization_entity != ''
            and organization_name != ''
        group by organization_entity, organization_name
    union
        select parent_organization_entity, parent_organization_name, FALSE
        from contribution_contribution
        where parent_organization_entity != ''
            and parent_organization_name != ''
        group by parent_organization_entity, parent_organization_name
    union
        select committee_entity, committee_name, FALSE
        from contribution_contribution
        where committee_entity != ''
            and committee_name != ''
        group by committee_entity, committee_name
    union
        select recipient_entity, recipient_name, FALSE
        from contribution_contribution
        where recipient_entity != ''
            and recipient_name != ''
        group by recipient_entity, recipient_name;
"""

# todo: modify alias query for attributes


@transaction.commit_on_success
def build_aggregates():
    cursor = connection.cursor()
    transaction.set_dirty()
    
    cursor.execute(aggregate_count_stmt)
    cursor.execute(aggregate_amount_given_stmt)
    cursor.execute(aggregate_amount_received_stmt)
    #cursor.execute(build_aliases_stmt)


class Command(BaseCommand):
    def handle(self, **args):
        build_aggregates()