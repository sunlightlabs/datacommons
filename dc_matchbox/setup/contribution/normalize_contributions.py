
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

"""
Create the string normalization tables for a database.
Relies on: contribution_organization_name column in contribution_contribution table.
"""

import MySQLdb
from strings.normalizer import basic_normalizer
from scripts.support.normalize_database import normalize
from settings import DATABASE_NAME, DATABASE_USER, DATABASE_HOST


connection = MySQLdb.connect(host=DATABASE_HOST, user=DATABASE_USER, db=DATABASE_NAME)
columns = [('contribution', ['contribution_organization_name'])]

normalize(connection, columns, basic_normalizer)