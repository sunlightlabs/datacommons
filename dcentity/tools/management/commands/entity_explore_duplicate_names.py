import re
import os
import urllib
from collections import defaultdict
from pprint import pprint
from itertools import combinations

from django.db import connection
from django.core.management.base import BaseCommand
from django.conf import settings

from dcentity.tools.names import PersonName, fix_name

class Command(BaseCommand):
    help = """
Prints a breakdown of all politicians whose names match exactly or
fuzzily, according to just what type of fuzziness the name matches
with, and whether the parties or states also match.

Results are returned as a table of total values, followed by the full
listing of all politicians per category.  This lists close to 40,000
entries; probably best redirect to less or a file to view.
"""

    def handle(self, *args, **kwargs):
        cursor = connection.cursor()
        cursor.execute("""
            SELECT DISTINCT a.entity_id,a.alias,m.state,m.party,m.seat FROM 
            matchbox_entityalias a 
            LEFT JOIN matchbox_politicianmetadata m ON m.entity_id=a.entity_id
            LEFT JOIN matchbox_entity e ON m.entity_id=e.id
            WHERE e.type = %s
            """, ['politician'])
        rows = cursor.fetchall()
        # Add person name classes
        rows = [(e, PersonName(fix_name(a or "")), s or "", p or "", o or "") for e,a,s,p,o in rows]
        by_last_name = defaultdict(list)
        for row in rows:
            by_last_name[row[1].last].append(row)
        count = 0
        grand_total = len(rows)
        totals = defaultdict(int)
        groups = defaultdict(list)
        for last_name, entities in by_last_name.iteritems():
            #print count, grand_total, last_name, len(entities)
            #count += len(entities)
            for eid1, name1, state1, party1, office1 in entities:
                for eid2, name2, state2, party2, office2 in entities:
                    # skip if we are the same, or if even maximal fuzziness fails
                    if eid1 == eid2 or not name1.matches(name2):
                        continue
                    state_checks = {
                        'same state': state1 == state2,
                        'diff state': state1 != state2,
                        'missing one state': (not state1 or not state2) and state1 != state2,
                        'missing two states': not state1 and not state2,
                    }
                    party_checks = {
                        'same party': party1 == party2,
                        'diff party; both 3rd': party1 not in "RD" and 
                            party2 not in "RD" and party1 != party2,
                        'diff party; one 3rd': party1 != party2 and
                            (party1 not in "RD" or party2 not in "RD") and
                            (party1 in "RD" or party2 in "RD"),
                        'diff party; R or D': party1 != party2 and
                            (party1 in "RD" and party2 in "RD"),
                    }
                    # Check all combinations of name matching conditions
                    all_conditions = ('missing_middle', 'nicknames', 'missing_suffix',
                            'initials', 'first_as_middle')

                    name_checks = {
                        'exact': name1.matches(name2, exact=True)
                    }

                    def check(conditions):
                        if len(conditions) == 0:
                            return name_checks['exact']
                        key = ", ".join(conditions)
                        name_checks[key] = name_checks.get(key, (
                            not check(conditions[:-1]) and 
                            name1.matches(name2, exact=True, **dict((c, True) for c in conditions))
                        ))
                        return name_checks[key]

                    def get_minimum_match():
                        for r in range(len(all_conditions)):
                            for conds in combinations(all_conditions, r):
                                if check(conds):
                                    return True
                    get_minimum_match()
                    
                    for n1, c1 in state_checks.iteritems():
                        if c1:
                            for n2, c2 in party_checks.iteritems():
                                if c2:
                                    for n3, c3 in name_checks.iteritems():
                                        if c3:
                                            key = " | ".join((n1, n2, n3))
                                            totals[key] += 1
                                            groups[key].append((
                                                (eid1, name1.name, state1, party1, office1),
                                                (eid2, name2.name, state2, party2, office2)
                                            ))
                                            # Only one name match per entity.
                                            break
        pprint(dict(totals))
        for group in sorted(groups.keys()):
            print group, len(groups[group])
            for n1, n2 in groups[group]:
                print " ", n1, n2
