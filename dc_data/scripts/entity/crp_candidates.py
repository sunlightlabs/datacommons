from hashlib import md5
from saucebrush import run_recipe
from saucebrush.sources import CSVSource
from saucebrush.filters import YieldFilter
from saucebrush.emitters import CSVEmitter, DebugEmitter
from strings.normalizer import basic_normalizer
import saucebrush
import datetime
import sys
import os

def extract_organizations(infile):
    
    now = datetime.datetime.utcnow().isoformat()
    
    run_recipe(
        CSVSource(infile),
        OrgSplitter(),
        EntityEmitter(open(FILENAME % 'entity', 'w'), now),
        EntityAttributeEmitter(open(FILENAME % 'entity_attribute', 'w')),
        EntityAliasEmitter(open(FILENAME % 'entity_alias', 'w')),
    )


if __name__ == "__main__":
    extract_organizations(sys.stdin)