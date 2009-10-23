from models import sql_names
from sql_utils import augment

def entity_search(connection, query):
    """
    Search for all entities with a normalized name prefixed by the normalized query string.
    
    Returns an iterator over triples (id, name, count).
    """
    
    stmt = "select e.%(entity_id)s, e.%(entity)s, count(*) \
        from %(entity)s e inner join individual_contributions c \
        on e.%(entity_id)s = c.employer_entity_id \
        where e.%(entity_name)s like '%(query)s%%' \
        group by e.%(entity_id)s order by count(*) desc;" % \
        augment(sql_names, query=query)
    return _execute_stmt(connection, stmt)


transaction_result_columns = ['Contrib', 'State', 'Orgname', 'Emp_EF', 'FecOccEmp', 'Date', 'Amount']

def transaction_search(connection, entity_id, result_columns=transaction_result_columns):
    """
    Search for all transactions that belong to a particular entity.
    
    Note: once transactions have donor and recipient entities in addition to employer entities
    this function will have to be adapted.
    """
    
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