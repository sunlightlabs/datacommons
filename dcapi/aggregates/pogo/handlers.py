from dcapi.aggregates.handlers import EntityTopListHandler



class TopContractorMisconductHandler(EntityTopListHandler):

    args = 'entity_id cycle'.split()
    fields = 'cycle contractor_entity contractor penalty_amount contracting_party instance misconduct_type'.split()

    stmt = """
        select cycle, contractor_entity, contractor, penalty_amount, contracting_party, instance, misconduct_type
        from agg_pogo_contractor_misconduct cm
        where
            contractor_entity = %s
            and cycle = %s
        order by penalty_amount desc, cycle desc
    """.format(', '.join(fields))

