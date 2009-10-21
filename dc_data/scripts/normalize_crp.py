

"""
Create the string normalization tables for a database.
Relies on: Orgname and Emp_EF fields in individual_contributions table.
Creates: SQL inserts file containing 'normalizations' table, with 'original' and 'normalization' columns.
"""

import MySQLdb
from normalizer import basic_normalizer
import normalize_database


connection = MySQLdb.connect(host='localhost', user='root', db='playground')
columns = [('individual_contributions', ['Orgname','Emp_EF'])]

normalize_database.normalize(connection, columns, basic_normalizer)