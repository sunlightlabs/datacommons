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
            count(distinct defennm) as defendants_count,
            array_to_string(array_agg(distinct d.defennm), ', ')as other_defendants,
            array_to_string(array_agg(distinct f.fcltcit || ', ' || f.fcltstc), '; ') as locations,
            array_to_string(array_agg(distinct f.fcltyad || ', ' || f.fcltcit || ', ' || f.fcltstc), '; ') as location_addresses,
            penalty,
            max_year,
            max_year_significance
        from agg_epa_echo_actions a
        inner join epa_echo_defendant d on a.case_num = d.enfocnu
        inner join epa_echo_facility f on a.case_num = f.enfocnu
        where
            entity_id = %s
            and cycle = %s
        group by cycle, case_num, case_name, defendant_name, entity_id, penalty, max_year, max_year_significance
        order by cycle desc, case when count(distinct defennm) = 1 then penalty else -1.0 / penalty end desc
        limit %s
    """.format(', '.join(fields))


