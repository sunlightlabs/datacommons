alter table matchbox_organizationmetadata add column is_corporation            boolean default('f');
alter table matchbox_organizationmetadata add column is_labor_org              boolean default('f');
alter table matchbox_organizationmetadata add column is_membership_org         boolean default('f');
alter table matchbox_organizationmetadata add column is_trade_assoc            boolean default('f');
alter table matchbox_organizationmetadata add column is_cooperative            boolean default('f');
alter table matchbox_organizationmetadata add column is_corp_w_o_capital_stock boolean default('f');

drop table if exists organization_metadata_latest_cycle_view;
create table organization_metadata_latest_cycle_view as
    select distinct on (entity_id)
        entity_id,
        cycle,
        lobbying_firm,
        parent_entity_id,
        industry_entity_id,
        subindustry_entity_id,
        is_superpac,
        is_corporation,
        is_labor_org,
        is_membership_org,
        is_trade_assoc,
        is_cooperative,
        is_corp_w_o_capital_stock
    from matchbox_organizationmetadata
    order by entity_id, cycle desc
;
