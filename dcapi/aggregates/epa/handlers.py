from dcapi.aggregates.handlers import EntityTopListHandler



class TopViolationActionsHandler(EntityTopListHandler):

    args = 'entity_id cycle'.split()
    fields = 'cycle case_name defendant_name defendant_entity amount year'.split()

    stmt = """
        select cycle, case_name, defendant_name, defendant_entity, amount, year--, location
        from agg_epa_echo_actions
        where
            defendant_entity = %s
            and cycle = %s
        order by cycle desc, amount desc
    """.format(', '.join(fields))


