from dcapi.aggregates.handlers import EntityTopListHandler, TopListHandler


class BundleHandler(EntityTopListHandler):
    args = 'entity_id entity_id entity_id cycle cycle limit'.split()
    fields = 'recipient_entity recipient_name recipient_type firm_entity firm_name lobbyist_entity lobbyist_name amount'.split()

    stmt = """
        select
            recipient_id,
            recipient_name,
            e.type as recipient_type,
            firm_id,
            firm_name,
            lobbyist_id,
            lobbyist_name,
            sum(coalesce(amount, 0))
        from
            agg_bundling b
            left join matchbox_entity e on b.recipient_id = e.id
        where
            (recipient_id = %s or firm_id = %s or lobbyist_id = %s)
            and case when %s = -1 then 1 = 1 else cycle = %s end
        group by
            recipient_id, recipient_name, e.type, firm_id, firm_name, lobbyist_id, lobbyist_name
        order by sum(coalesce(amount, 0)) desc
        limit %s
    """
    #from faca_records, (values (%s::uuid, %s, %s::integer)) as params (entity_id, agency, cycle)


class RecipientExplorerHandler(TopListHandler):
    
    args = 'cycle cycle'.split()
    fields = "recipient_name recipient_id total count".split()
    
    stmt = """
        select recipient_name, recipient_id, sum(amount) as total_amount, count(*)
        from agg_bundling
        where
            %s = -1 or cycle = %s
        group by recipient_name, recipient_id
        order by total_amount desc
    """
    
class FirmExplorerHandler(TopListHandler):

    args = 'cycle cycle'.split()
    fields = "recipient_name recipient_id total count".split()

    stmt = """
        select firm_name, firm_id, sum(amount) as total_amount, count(*)
        from agg_bundling
        where
            %s = -1 or cycle = %s
        group by firm_name, firm_id
        order by total_amount desc
    """

class DetailExplorerHandler(TopListHandler):
    
    args = 'cycle cycle name name name'.split()
    fields = 'recipient_name recipient_id firm_name firm_id lobbyist_name lobbyist_id total_amount count'.split()
    
    stmt = """
        select recipient_name, recipient_id, firm_name, firm_id, lobbyist_name, lobbyist_id, sum(amount) as total_amount, count(*)
        from agg_bundling
        where
            (%s = -1 or cycle = %s)
            and (recipient_name = %s or firm_name = %s or lobbyist_name = %s)
        group by recipient_name, recipient_id, firm_name, firm_id, lobbyist_name, lobbyist_id
        order by total_amount desc
    """

    def read(self, request, **kwargs):
        kwargs.update({'name': request.GET.get('name', '')})
        
        return super(DetailExplorerHandler, self).read(request, **kwargs)
        
    