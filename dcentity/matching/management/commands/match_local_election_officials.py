from dcentity.matching.management.base.matching import MatchingCommand
from dcentity.matching.models import LocalElectionOfficial, ContributorsByStateForLEO
from dcentity.models import Entity
from django.db.models import F

import re

STATE_NAMES_STR = """Alabama,AL
Alaska,AK
Arizona,AZ
Arkansas,AR
California,CA
Colorado,CO
Connecticut,CT
Delaware,DE
Florida,FL
Georgia,GA
Hawaii,HI
Idaho,ID
Illinois,IL
Indiana,IN
Iowa,IA
Kansas,KS
Kentucky,KY
Louisiana,LA
Maine,ME
Maryland,MD
Massachusetts,MA
Michigan,MI
Minnesota,MN
Mississippi,MS
Missouri,MO
Montana,MT
Nebraska,NE
Nevada,NV
New Hampshire,NH
New Jersey,NJ
New Mexico,NM
New York,NY
North Carolina,NC
North Dakota,ND
Ohio,OH
Oklahoma,OK
Oregon,OR
Pennsylvania,PA
Rhode Island,RI
South Carolina,SC
South Dakota,SD
Tennessee,TN
Texas,TX
Utah,UT
Vermont,VT
Virginia,VA
Washington,WA
West Virginia,WV
Wisconsin,WI
Wyoming,WY
American Samoa,AS
District of Columbia,DC
Federated States of Micronesia,FM
Guam,GU
Marshall Islands,MH
Northern Mariana Islands,MP
Palau,PW
Puerto Rico,PR
Virgin Islands,VI"""

STATE_NAME_ROWS = STATE_NAMES_STR.split("\n")
STATE_NAMES = dict([ x.split(',') for x in STATE_NAME_ROWS ])

class Command(MatchingCommand):


    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.subject = LocalElectionOfficial.objects.all()
        self.subject_id_type = 'integer'

        self.match = ContributorsByStateForLEO.objects.all()
        self.match_table_prefix = 'leo'
        self.match_id_type = 'integer'

    def get_potential_matches_for_subject(self, subject_name, subject_obj):
        """
            Takes a name cleaver object and ideally returns a loosely matched set of objects
            which we can then filter more stringently by scoring
        """

        key = '_'.join([subject_name.last, subject_obj.state])
        key = re.sub(r'[^-a-zA-Z0-9,.\'"^&*()]', '', key)
        key = key.lower().encode('ascii', 'replace')
        objs = self.mc.get(key)
        if not objs:
            try:
                state_abbr = STATE_NAMES[subject_obj.state]
                objs = self.match.filter(state=STATE_NAMES.get(subject_obj.state)).filter(**{'{0}__{1}'.format(self.match_name_attr, self.match_operator): subject_name.last})
                self.mc.set(key, objs)
            except KeyError:
                raise 'Uh oh, could not find an abbreviation for state: {}'.format(subject_obj.state)

        return objs

    def get_metadata_confidence(self, match_obj, subject_obj):
        metadata_confidence = 0
        if re.match(r'(?i).*(electio|clerk)', ' '.join([match_obj.employer, match_obj.occupation])) \
                or re.match(r'.*BOE', ' '.join([match_obj.employer, match_obj.occupation])):
            metadata_confidence += 1
        elif re.match(r'(?i).*(town|cty|county|city)', ' '.join([match_obj.employer, match_obj.occupation])):
            metadata_confidence += 0.5

        return metadata_confidence



