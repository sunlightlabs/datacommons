from dcentity.matching.management.base.matching import MatchingCommand
from dcentity.matching.models import MemberOfCongressWithBioguide
from dcentity.models import Entity
from django.db.models import Q


class Command(MatchingCommand):

    confidence_threshold = 1.1

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.subject = MemberOfCongressWithBioguide.objects
        self.subject_id_type = 'integer'
        self.match = Entity.objects.filter(type='politician', attributes__namespace='urn:crp:recipient')
        self.match_table_prefix = 'bioguide_historical'
        self.match_name_attr = 'name'

    def get_potential_matches_for_subject(self, subject_name, subject_obj):
        """
            Takes a name cleaver object and ideally returns a loosely matched set of objects
            which we can then filter more stringently by scoring
        """
        if not subject_obj.district:
            district_q = Q(politician_metadata_by_cycle__district_held__isnull=True) | Q(politician_metadata_by_cycle__district_held__in=['', '_'])
        else:
            district_str = '{0}-{1}'.format(subject_obj.state, subject_obj.padded_district)
            district_q = Q(politician_metadata_by_cycle__district_held=district_str)

        matches = self.match.filter(
            district_q,
            politician_metadata_by_cycle__cycle=subject_obj.cycle,
            politician_metadata_by_cycle__state_held=subject_obj.state,
            aliases__alias__icontains=subject_name.last,
        ).distinct()

        return matches

    NICKNAMES = (
        ('Allan', 'Allen', 'Alan', 'Al'),
        ('Andre', u'Andr\00e9'),
        ('Andrew', 'Andy', 'Drew'),
        ('Antonio', 'Anthony', 'Tony', 'Anton'),
        ('Barbara', 'Barb'),
        ('Bernard', 'Bernie'),
        ('Calvin', 'Cal'),
        ('Charles', 'Chas', 'Chuck', 'Chucky'),
        ('Christine', 'Christina', 'Chris'),
        ('Christopher', 'Chris'),
        ('Daniel', 'Dan', 'Danny'),
        ('David', 'Dave'),
        ('Donald', 'Don', 'Donny'),
        ('Douglas', 'Doug'),
        ('Edward', 'Ed', 'Eddie'),
        ('Francis', 'Frank', 'Frankie'),
        ('Fredrick', 'Frederick', 'Fred', 'Freddy'),
        ('Gerard', 'Gerry', 'Jerry'),
        ('Gregory', 'Greg'),
        ('Harris', 'Harry', 'Harrison'),
        ('Henry', 'Hank'),
        ('Herbert', 'Herb'),
        ('Howard', 'Howie'),
        ('James', 'Jim', 'Jimmy'),
        ('Jerome', 'Jerry'),
        ('John', 'Jon', 'Johnny', 'Jack'),
        ('Joseph', 'Joe'),
        ('Lawrence', 'Laurence', 'Larry'),
        ('Lewis', 'Louis', 'Lou'),
        ('Martin', 'Marty'),
        ('Melvin', 'Melvyn' ,'Mel'),
        ('Mervyn', 'Merv'),
        ('Michael', 'Mike'),
        ('Mitchell', 'Mitch'),
        ('Patricia', 'Pat', 'Patty', 'Pati'),
        ('Patrick', 'Pat'),
        ('Peter', 'Pete'),
        ('Philip', 'Phillip', 'Phil'),
        ('Randall', 'Randy'),
        ('Richard', 'Rick', 'Dick', 'Rich'),
        ('Robert', 'Rob', 'Robby', 'Bobby', 'Bob'),
        ('Steven', 'Stephen', 'Steve'),
        ('Stewart', 'Stuart', 'Stu'),
        ('Terrance', 'Terry'),
        ('Thomas', 'Tom', 'Thom', 'Tommy'),
        ('William', 'Bill', 'Billy', 'Will', 'Willy'),
        ('Willis', 'Will'),
    )

    def get_confidence(self, name1, name2):
        score = 0

        # score last name
        if name1.last == name2.last:
            score += 1
        else:
            return 0

        # score first name
        if name1.first == name2.first:
            score += 1
        else:
            for name_set in self.NICKNAMES:
                if set(name_set).issuperset([name1.first, name2.first]):
                    score += 0.6
                    break

            if name1.first == name2.middle and name2.first == name1.middle:
                score += 0.8
            elif name1.first[0] == name2.first[0]:
                score += 0.1

        # score middle name
        if name1.middle and name2.middle:
            if name1.middle == name2.middle:
                score += 1
            elif name1.middle[0] == name2.middle[0]:
                score += .5
            else:
                score -= 1.5

        return score

