

"""
Create the string normalization tables for a database.
Relies on: contribution_organization_name column in contribution_contribution table.
"""

from strings.normalizer import basic_normalizer
from matchbox_scripts.support.normalize_database import normalize

columns = [('entityalias', ['entityalias_alias'])]

def run():
    normalize(columns, basic_normalizer)
    

if __name__ == "main":
    run()