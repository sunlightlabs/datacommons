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

class SenateIndExpLatLongHandler(TopListHandler):
    
    args = ['cycle']
    fields = 'state amount latitude longitude party'.split()

    stmt = """
        select
            candidate_state,
            sum(amount) as amount,
            latitude,
            longitude,
            --case when party = 'D' then latitude + 1.1 else latitude - 1.1 end as latitude,
            --case when party = 'R' then longitude + 0.8 else longitude - 0.8 end as longitude,
            party
        from (
        select
            candidate_state,
            sum(amount) as amount,
            case when ((candidate_party = 'Dem' and support_oppose = 'Support') or (candidate_party = 'Rep' and support_oppose = 'Oppose')) then 'D' else 'R' end as party
        from fec_indexp
        where
            candidate_office = 'S'
            --and ((candidate_party = 'Rep' and support_oppose = 'Support') or (candidate_party = 'Dem' and support_oppose = 'Oppose'))
            and extract(year from date) >= %s
        group by
            candidate_state, candidate_party, support_oppose
        )x
        left join state_lat_long on state = candidate_state
        group by candidate_state, latitude, longitude, party
        having sum(amount) > 50000
    """
    
