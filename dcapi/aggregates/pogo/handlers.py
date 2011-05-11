from dcapi.aggregates.handlers import EntityTopListHandler



class TopContractorMisconductHandler(EntityTopListHandler):

    args = 'entity_id year limit'.split()
    fields = 'date_year contractor instance penalty_amount contracting_party misconduct_type'.split()
    stmt = """
        select {0}
        from pogo_contractormisconduct cm
        inner join pogo_contractormisconduct_associations cma
            on cm.id = cma.contractormisconduct_id
        inner join matchbox_entity me
            on me.id = cma.entity_id
        where
            me.id = %s
            and date_year = %s
        limit %s
        order by penalty_amount desc, date_year desc
    """.format(', '.join(fields))

