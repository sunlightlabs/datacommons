

"""
Create the string normalization tables for a database.
Relies on: contribution_organization_name column in contribution_contribution table.
"""

from strings.normalizer import basic_normalizer
from matchbox_scripts.support.normalize_database import normalize
from matchbox.models import sql_names

def run():
    normalize(sql_names['entityalias'], sql_names['entityalias_alias'], basic_normalizer)
    

if __name__ == "main":
    run()