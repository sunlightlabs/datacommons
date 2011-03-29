from django.core.management.base import CommandError, BaseCommand
from django.db                   import connections, transaction
from name_cleaver.name_cleaver   import PoliticianNameCleaver, RunningMatesNames
from optparse                    import make_option

import datetime

class MatchingCommand(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option("-b", "--begin_at_count", dest="begin_at_count", \
            help="Number to resume script at", metavar="INTEGER", default=1),
        make_option("-t", "--table", dest="table", help="Table to store matches in", metavar="STRING"),
    )

    def __init__(self, *args, **kwargs):
        super(MatchingCommand, self).__init__(*args, **kwargs)
        self.subject = None
        self.subject_name_attr = 'name'
        self.subject_id_type = 'uuid'
        self.match = None
        self.match_table_prefix = None
        self.match_name_attr = 'name'
        self.match_id_type = 'uuid'

    @transaction.commit_manually
    def handle(self, *args, **options):

        if not (self.subject and self.match and self.match_table_prefix):
            raise 'You must define self.subject, self.match and self.match_table_prefix in the subclass.'

        count = self.subject.objects.count()
        begin_at = int(options['begin_at_count'])
        table = options['table'] or self.generate_table_name()

        cursor = connections['default'].cursor()
        if options.has_key('table') and options['table']:
            print 'Resuming with table {0}'.format(table)
        else:
            print 'Creating table {0}'.format(table)
            cursor.execute('create table {0} (id serial primary key, subject_id {1} not null, match_id {2} not null, confidence numeric not null)'.format(table, self.subject_id_type, self.match_id_type))
            transaction.commit()

        for i, subject in enumerate(self.subject.objects.all()[begin_at-1:]):

            print "{0}/{1}: {2}".format(begin_at+i, count, getattr(subject, self.subject_name_attr))
            #pre-process subject name
            subject_raw_name = self.preprocess_subject_name(getattr(subject, self.subject_name_attr))
            subject_name = PoliticianNameCleaver(subject_raw_name).parse()

            if isinstance(subject_name, RunningMatesNames) or not subject_name.last:
                continue

            # search match entities
            potential_matches = self.match.filter(**{'{0}__icontains'.format(self.match_name_attr): subject_name.last})
            print 'Potential matches: {0}'.format(potential_matches.count())

            for match in potential_matches:
                match_name = PoliticianNameCleaver(getattr(match, self.match_name_attr)).parse()

                if isinstance(match_name, RunningMatesNames):
                    for running_mate_name in match_name.mates():
                        confidence = self.get_confidence(running_mate_name, subject_name)
                else:
                    confidence = self.get_confidence(match_name, subject_name)

                if confidence >= 2:
                    self.insert_match(cursor, table, match, subject, confidence)

                transaction.commit()

        print 'Done. Records were inserted into {0}.'.format(table)


    def preprocess_subject_name(self, name):
        return name


    def get_confidence(self, name1, name2):
        score = 0
        if name1.last == name2.last:
            score += 1
        else:
            return 0

        if name1.first == name2.first:
            score += 1
        else:
            return 0

        if name1.middle and name2.middle:
            if name1.middle == name2.middle:
                score += 1
            elif name1.middle[0] == name2.middle[0]:
                score += .5
            else:
                score -= 1.5

        return score


    def insert_match(self, cursor, table_name, match, subject, confidence):
        #print 'Inserting.'
        cursor.execute("insert into {0} (subject_id, match_id, confidence) values ('{1}', '{2}', {3})".format(table_name, subject.id, match.id, confidence))


    def generate_table_name(self):
        date_time_now = datetime.datetime.now().strftime('%Y%m%d_%H%M')
        return '_'.join([self.match_table_prefix, 'matches', date_time_now])



