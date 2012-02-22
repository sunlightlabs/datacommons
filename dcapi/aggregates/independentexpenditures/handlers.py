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
