from dcapi.aggregates.handlers import EntityTopListHandler


class CandidateIndExpHandler(EntityTopListHandler):
        
    args = ['entity_id']    
    fields = "committee_name committee_entity support_oppose amount".split()
    
    stmt = """
        select committee_name, committee_entity, support_oppose, amount
        from agg_fec_indexp
        where
            candidate_entity = %s
        order by amount desc
    """


class CommitteeIndExpHandler(EntityTopListHandler):

    args = ['entity_id']    
    fields = "candidate_name candidate_entity support_oppose amount".split()

    stmt = """
        select candidate_name, candidate_entity, support_oppose, amount
        from agg_fec_indexp
        where
            committee_entity = %s
        order by amount desc
    """

class CommitteeTopContribsHandler(EntityTopListHandler):
    
    args = ['entity_id', 'limit']
    fields = "contributor_name date amount".split()
    
    stmt = """
        select contributor_name, date, amount
        from fec_committee_itemized i
        inner join matchbox_entityattribute a on i.committee_id = a.value and a.namespace = 'urn:fec_committee'
        where
            a.entity_id = %s
        order by amount desc
        limit %s
    """