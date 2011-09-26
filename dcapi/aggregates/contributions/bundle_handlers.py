from dcapi.aggregates.handlers import EntityTopListHandler


class BundleHandler(EntityTopListHandler):
    args = 'entity_id entity_id entity_id cycle cycle limit'.split()
    fields = 'recipient_entity recipient_name firm_entity firm_name lobbyist_entity lobbyist_name amount'.split()

    stmt = """
        select
            recipient_id,
            recipient_name,
            firm_id,
            firm_name,
            lobbyist_id,
            lobbyist_name,
            sum(coalesce(amount, 0))
        from
            agg_bundling
        where
            (recipient_id = %s or firm_id = %s or lobbyist_id = %s)
            and case when %s = -1 then 1 = 1 else cycle = %s end
        group by
            recipient_id, recipient_name, firm_id, firm_name, lobbyist_id, lobbyist_name
        order by sum(coalesce(amount, 0)) desc
        limit %s
    """
    #from faca_records, (values (%s::uuid, %s, %s::integer)) as params (entity_id, agency, cycle)

