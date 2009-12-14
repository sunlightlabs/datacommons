#!/usr/bin/env python
from hashlib import md5
from saucebrush import run_recipe
from saucebrush.sources import CSVSource
from saucebrush.filters import YieldFilter, Filter
from strings.normalizer import basic_normalizer
from util import EntityEmitter, EntityAliasEmitter, EntityAttributeEmitter
import saucebrush
import datetime
import sys
import os
"""
    python contrib_orgs.py < [path to denorm csv]
    *** just writes to . directory for now ***
"""

FILENAME = u"contrib_orgs_%s.csv"
NAMESPACE = u"urn:matchbox:organization"

def gen_id(org_name):
    urn = '%s:%s' % (NAMESPACE, basic_normalizer(org_name.decode('utf-8', 'ignore')))
    return md5(urn).hexdigest()

class UniqueNameFilter(Filter):
    
    def __init__(self):
        super(UniqueNameFilter, self).__init__();
        self._cache = {}
        
    def process_record(self, record):
        if record['name'] not in self._cache:
            self._cache[record['name']] = None
            return record
            
class UniqueIDFilter(Filter):

    def __init__(self):
        super(UniqueIDFilter, self).__init__();
        self._cache = {}

    def process_record(self, record):
        if record['id'] not in self._cache:
            self._cache[record['id']] = None
            return record

class ParentChildOrgSplitter(YieldFilter):
    
    def process_record(self, record):
        for key in ('organization_name', 'parent_organization_name'):
            org_name = record[key].strip()
            if org_name:
                yield {
                    'id': gen_id(org_name),
                    'name': org_name,
                }


def extract_organizations(infile):
    
    now = datetime.datetime.utcnow().isoformat()
    
    run_recipe(
        CSVSource(infile),
        ParentChildOrgSplitter(),
        UniqueNameFilter(),
        EntityAliasEmitter(open(FILENAME % 'entity_alias', 'w')),
        UniqueIDFilter(),
        EntityEmitter(open(FILENAME % 'entity', 'w'), now),
        EntityAttributeEmitter(open(FILENAME % 'entity_attribute', 'w')),
    )


if __name__ == "__main__":
    extract_organizations(sys.stdin)