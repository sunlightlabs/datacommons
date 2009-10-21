

"""
Populate the entities table based on string equality of transaction names.
"""

from build_entities import populate_entities
        
        
data_model = {'table_normalizations': 'normalizations', 
                     'column_normalizations_original': 'Original',
                     'table_entities': 'entities',
                     'column_entities_id': 'id',
                     'column_entities_name': 'name',
                     'table_transactions': 'individual_contributions',
                     'column_transactions_employer_id': 'employer_entity_id',
                     'column_transactions_name': 'Orgname'}        
        
        
if __name__ == '__main__': 
    connection = MySQLdb.connect(host='localhost', user='root', db='playground')
    populate_entities(connection, data_model)
