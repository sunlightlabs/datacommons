

def entity_search(connection, query):
    """
    Search for all entities with a normalized name prefixed by the normalized query string.
    
    Returns an iterator over a triple (id, name, count)
    """
    
    stmt = "select e.id, e.name, count(*) \
            from entities e inner join individual_contributions c \
            on e.id = c.employer_entity_id \
            where e.name like '%(query)s%%' \
            group by e.id order by count(*) desc;" % \
            {'query': query}
    return _execute_stmt(connection, stmt)


transaction_result_columns = ['Contrib', 'State', 'Orgname', 'Emp_EF', 'FecOccEmp', 'Date', 'Amount']

def transaction_search(connection, entity_id, result_columns=transaction_result_columns):
    stmt = "select %(result_columns)s \
            from individual_contributions \
            where employer_entity_id = %(entity_id)s \
            order by amount desc" % \
            {'result_columns': ",".join(result_columns), 'entity_id': int(entity_id)}
    return _execute_stmt(connection, stmt)


def _execute_stmt(connection, stmt):
    cursor = connection.cursor()
    cursor.execute(stmt)
    return cursor