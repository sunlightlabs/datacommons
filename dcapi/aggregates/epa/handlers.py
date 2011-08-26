from dcapi.aggregates.handlers import EntityTopListHandler



class TopViolationActionsHandler(EntityTopListHandler):
    fields = 'cycle case_id case_name defendant_name entity_id defendants_count other_defendants locations location_addresses amount year date_significance'.split()

    stmt = """
        select
            cycle,
            case_num,
            case_name,
            defendant_name,
            entity_id,
            num_defendants,
            defendants,
            locations,
            location_addresses,
            penalty,
            year,
            last_date_significance
        from agg_epa_echo_actions a
        where
            entity_id = %s
            and cycle = %s
        order by rank
        limit %s
    """.format(', '.join(fields))


