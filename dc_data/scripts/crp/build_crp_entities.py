

"""
Populate the entities table based on string equality of transaction names.
"""

from build_entities import populate_entities
        
        

if __name__ == '__main__': 
    connection = MySQLdb.connect(host='localhost', user='root', db='playground')
    populate_entities(connection, data_model)
