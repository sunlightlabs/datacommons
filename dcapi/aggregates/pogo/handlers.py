from dcapi.aggregates.handlers import EntityTopListHandler



class TopContractorMisconductHandler(EntityTopListHandler):

    args = 'entity_id cycle'.split()
    fields = 'cycle year date_significance contractor_entity contractor penalty_amount contracting_party instance disposition misconduct_type misconduct_url'.split()

    stmt = """
        select cycle, year, date_significance, contractor_entity, contractor, penalty_amount, contracting_party, instance, disposition, misconduct_type, misconduct_url
        from agg_pogo_contractor_misconduct cm
        where
            contractor_entity = %s
            and cycle = %s
        order by cycle desc, penalty_amount desc
    """.format(', '.join(fields))

