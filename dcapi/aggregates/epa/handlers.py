from dcapi.aggregates.handlers import EntityTopListHandler



class TopViolationActionsHandler(EntityTopListHandler):

    args = 'entity_id cycle'.split()
    fields = 'cycle case_name defendant amount date location'.split()

    stmt = """
        select cycle, case_name, defendant, amount, date, location
        from agg_epa_actions cm
        where
            organization_entity = %s
            and cycle = %s
        order by cycle desc, amount desc
    """.format(', '.join(fields))


