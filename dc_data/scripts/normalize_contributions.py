
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

"""
Create the string normalization tables for a database.
Relies on: Orgname and Emp_EF fields in individual_contributions table.
Creates: SQL inserts file containing 'normalizations' table, with 'original' and 'normalization' columns.
"""

import MySQLdb
from normalizer import basic_normalizer
from scripts.normalize_database import normalize
from settings import DATABASE_NAME, DATABASE_USER, DATABASE_HOST


connection = MySQLdb.connect(host=DATABASE_HOST, user=DATABASE_USER, db=DATABASE_NAME)
columns = [('contribution', ['contribution_organization_name'])]

normalize(connection, columns, basic_normalizer)