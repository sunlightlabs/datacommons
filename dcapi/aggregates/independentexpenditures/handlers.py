from dcapi.aggregates.handlers import EntityTopListHandler


class CandidateIndExpHandler(EntityTopListHandler):
        
    args = ['entity_id', 'cycle']    
    fields = "committee_name committee_entity support_oppose amount".split()
    
    stmt = """
        select committee_name, committee_entity, support_oppose, amount
        from agg_fec_indexp
        where
            candidate_entity = %s
            and cycle = %s
        order by amount desc
    """


class CommitteeIndExpHandler(EntityTopListHandler):

    args = ['entity_id', 'cycle']    
    fields = "candidate_name candidate_entity support_oppose amount".split()

    stmt = """
        select candidate_name, candidate_entity, support_oppose, amount
        from agg_fec_indexp
        where
            committee_entity = %s
            and cycle = %s
        order by amount desc
    """

    
class CandidateIndExpDownloadHandler(EntityTopListHandler):
    
    args = ['entity_id', 'cycle']
    fields = "candidate_id candidate_name spender_id spender_name election_type candidate_state \
        candidate_district candidate_office candidate_party \
        amount aggregate_amount support_oppose purpose \
        payee filing_number amendment transaction_id image_number received_date".split()
        

    stmt = """
        select candidate_id, candidate_name, spender_id, spender_name, election_type, candidate_state,
            candidate_district, candidate_office, candidate_party, 
            amount, aggregate_amount, support_oppose, purpose, 
            payee, filing_number, amendment, transaction_id, image_number, received_date
        from fec_indexp i
        inner join agg_fec_indexp_candidates a using (cycle, spender_id, filing_number, transaction_id)
        where
            a.entity_id = %s
            and cycle = %s
        order by spender_name, date, amount desc
    """
    
class CommitteeIndExpDownloadHandler(EntityTopListHandler):
    
    args = ['entity_id', 'cycle']
    fields = "candidate_id candidate_name spender_id spender_name election_type candidate_state \
        candidate_district candidate_office candidate_party \
        amount aggregate_amount date support_oppose purpose \
        payee filing_number amendment transaction_id image_number received_date".split()
        

    stmt = """
        select candidate_id, candidate_name, spender_id, spender_name, election_type, candidate_state,
            candidate_district, candidate_office, candidate_party, 
            amount, aggregate_amount, date, support_oppose, purpose, 
            payee, filing_number, amendment, transaction_id, image_number, received_date
        from fec_indexp i
        inner join agg_fec_indexp_committees a using (cycle, spender_id)
        where
            a.entity_id = %s
            and cycle = %s
        order by candidate_name, date, amount desc
    """
