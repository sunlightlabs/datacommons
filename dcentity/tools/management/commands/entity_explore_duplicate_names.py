import csv
from collections import defaultdict
from pprint import pprint
from itertools import combinations
from cStringIO import StringIO

from django.db import connection
from django.core.management.base import BaseCommand

from dcentity.tools.names import PersonName, fix_name

class Command(BaseCommand):
    help = """
Prints a breakdown of all politicians whose names match exactly or
fuzzily, according to just what type of fuzziness the name matches
with, and whether the parties or states also match.

Results are presented in one of two ways:

    trusted:  If the argument "trusted" is provided, only those match types
        which are coded in the source code as "trusted" will be returned.
        Results are printed as CSV with the following format:

        <-------   entity one  ------>  <------  entity two  -------->
        id, name, state, party, office, id, name, state, party, office

        Details like name, state, party, and office are included to allow
        visual inspection of the file.

    possible: Those entries which are "possibly" trusted are returned -- they
        should receive more scrutiny.

    full: If 'full' or no argument is provided, full results will be printed,
        intended for visual inspection.  Results are printed as a table of
        total values, followed by the full listing of all politicians per
        category.  This lists close to 40,000 entries; probably best redirect
        to less or a file to view.

"""

    # Totally trusted results
    trusted = [
            "same state | same party | exact",
            "missing one state | same party | exact",
            "same state | diff party; both 3rd | exact",
    ]
    # Possbly trusted results
    possible = [
            "same state | same party | missing_middle", # Watch out for George W Bush
            "same state | same party | nicknames",
            "same state | same party | initials",
            "same state | same party | missing_suffix",
    ]

    # Any name matching exactly those in here, with the listed conditions, will be
    # excluded from 'trusted' and 'possible', even if they would otherwise be
    # included.
    excluded = set([
        "George Bush",
    ])


    def handle(self, *args, **kwargs):
        if len(args) > 0:
            if args[0] in ("trusted", "possible", "full"):
                display = args[0]
            else:
                print "Unexpected argument '%s'.  Options are 'trusted' or 'full'" % args[0]
                return
        else:
            display = 'full'

        cursor = connection.cursor()
        # ORM is way too slow for this on 100,000+ rows.
        cursor.execute("""
            SELECT DISTINCT a.entity_id,a.alias,m.state,m.party,m.seat FROM
            matchbox_entityalias a
            LEFT JOIN politician_metadata_latest_cycle_view m ON m.entity_id=a.entity_id
            LEFT JOIN matchbox_entity e ON m.entity_id=e.id
            WHERE e.type = %s
            """, ['politician'])
        rows = cursor.fetchall()
        # Add person name classes
        rows = [(e, PersonName(fix_name(a or "")), s or "", p or "", o or "") for e,a,s,p,o in rows]
        by_last_name = defaultdict(list)

        # group all entities by last name
        for row in rows:
            by_last_name[row[1].last].append(row)

        #count = 0
        #grand_total = len(rows)
        totals = defaultdict(int)
        groups = defaultdict(list)

        for last_name, entities in by_last_name.iteritems():
            #print count, grand_total, last_name, len(entities)
            #count += len(entities)

            # for each last name, split enities into a groups of state and federal politicians
            # this will make all the "left sides" of the matches federal and all the right sides state
            fed_entities =  [ entity for entity in entities if entity[4].startswith('federal') ]
            state_entities =  [ entity for entity in entities if entity[4].startswith('state') ]

            for eid1, name1, state1, party1, office1 in fed_entities:

                for eid2, name2, state2, party2, office2 in state_entities:
                    # skip if maximal fuzziness fails
                    if not name1.matches(name2):
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



        if display == 'full':
            pprint(dict(totals))
            for group in sorted(groups.keys()):
                print group, len(groups[group])
                for n1, n2 in groups[group]:
                    print " ", n1, n2
        elif display in ('trusted', 'possible'):
            out = StringIO()
            writer = csv.writer(out)
            matches = getattr(self, display)
            for group in matches:
                for n1, n2 in groups[group]:
                    if not n1[1] in self.excluded and not n2[1] in self.excluded:
                        if "federal" in n2[-1]:
                            writer.writerow(n2 + n1)
                        else:
                            writer.writerow(n1 + n2)
            print out.getvalue()
            out.close()

