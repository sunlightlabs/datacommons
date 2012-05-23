from dcapi.aggregates.handlers import EntityTopListHandler, TopListHandler


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

    
class CandidateIndExpDownloadHandler(EntityTopListHandler):
    
    args = ['entity_id']
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
        inner join agg_fec_indexp_candidates a using (spender_id, filing_number, transaction_id)
        where
            a.entity_id = %s
        order by spender_name, date, amount desc
    """

class TopPACsByIndExpsHandler(TopListHandler):
    args = ['cycle', 'limit']

    fields = 'name entity_id amount cycle'.split()

    stmt = """
        select name, entity_id, spending_amount as amount, cycle
        from agg_fec_indexp_totals
        inner join matchbox_entity on matchbox_entity.id = agg_fec_indexp_totals.entity_id
        where cycle = %s
        order by spending_amount desc
        limit %s
    """

class CommitteeIndExpDownloadHandler(EntityTopListHandler):
    
    args = ['entity_id']
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
        inner join agg_fec_indexp_committees a using (spender_id)
        where
            a.entity_id = %s
        order by candidate_name, date, amount desc
    """
    