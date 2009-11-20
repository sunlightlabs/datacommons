
"""
Take an existing Contributions database and add all the matchbox-specific tables.

Specifically:
1. removes existing matchbox tables and columns
2. runs Django syncdb
3. runs build_contribution_entities.py
4. creates the indicies on the entity-related tables
5. runs normalize_contributions.py
6. creates the indicies on normalizations

Assumes that the contributions table already has any necessary indicies.
"""


import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
#import settings
from django.core.management import execute_from_command_line


"""
As far as I can tell, there's a bug in MySQLdb or Django that sometimes
causes the Django connection to throw an error:
    _mysql_exceptions.InterfaceError: (0, '')
Creating our own connection seems to solve the problem.
"""
from django.db import connection

from matchbox.models import sql_names
from matchbox_scripts.contribution.build_contribution_entities import run as build_entities
from matchbox_scripts.contribution.normalize_contributions import run as build_normalizations


def drop_model(model_name):
    cursor.execute("select exists (select * from information_schema.tables where table_name = %s)", [sql_names[model_name]])
    if  cursor.__iter__().next()[0]:
        cursor.execute("drop table %s" % sql_names[model_name])


def build_matchbox():
    
    print("Clearing and rebuilding tables...")
    for model_name in ['entityalias', 'entityattribute', 'entitynote', 'mergecandidate', 'normalization', 'entity']:
        drop_model(model_name)
    execute_from_command_line(["manage.py", "syncdb"])

    print("Building entities...")
    build_entities()
    
    print("Indexing aliases...")
    cursor = connection.cursor()
    cursor.execute("create index entityalias_alias_index on %(entityalias)s (%(entityalias_alias)s)" % sql_names)
    
    print("Building normalizations...")
    build_normalizations()
    
    print("Indexing normalizations...")
    cursor.execute("create index normalization_normalized_index on %(normalization)s (%(normalization_normalized)s)" % sql_names)
    cursor.execute("create index normalization_original_fulltext on %(normalization)s using gin(to_tsvector('simple', %(normalization_original)s))" % sql_names)


if __name__ == "__main__":
    cursor = connection.cursor()
    build_matchbox()