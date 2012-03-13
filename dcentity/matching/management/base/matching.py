from django.core.management.base import CommandError, BaseCommand
from django.db.utils             import DatabaseError
from django.db                   import connections, transaction
from name_cleaver                import PoliticianNameCleaver, RunningMatesNames
from optparse                    import make_option

import datetime
import pylibmc
import re
import sys

class MatchingCommand(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option("-b", "--begin-at-count",
            dest="begin_at_count",
            help="Number to resume script at",
            metavar="INTEGER",
            default=1
        ),
        make_option("-t", "--table",
            dest="table",
            help="Table to store matches in",
            metavar="STRING"
        ),
        make_option("-n", "--insert-non-matches",
            dest="insert_non_matches",
            action='store_true',
            help="Store subjects with no potential matches in the table with a confidence of -1.",
        ),
        make_option("-I", "--do-post-insert",
            dest="do_post_insert",
            help="Perform extra processing after match insertion"
        )
    )

    name_cleaver = PoliticianNameCleaver
    confidence_threshold = 2

    def __init__(self, *args, **kwargs):
        super(MatchingCommand, self).__init__(*args, **kwargs)
        self.subject = None
        self.subject_name_attr = 'name'
        self.subject_id_type = 'uuid'

        self.match = None
        self.match_table_prefix = None
        self.match_name_attr = 'name'
        self.match_id_type = 'uuid'

        self.match_operator = 'icontains'

        self.mc = pylibmc.Client(['127.0.0.1:11211'])

    @transaction.commit_on_success
    def handle(self, *args, **options):

        if not (self.subject and self.match and self.match_table_prefix):
            transaction.rollback()
            raise CommandError('You must define self.subject, self.match and self.match_table_prefix in the subclass.')

        count = self.subject.count()
        begin_at = int(options['begin_at_count'])
        table = options['table'] or self.generate_table_name()

        cursor = connections['default'].cursor()
        if options.has_key('table') and options['table']:
            print 'Resuming with table {0}'.format(table)
        else:
            try:
                print 'Creating table {0}'.format(table)
                cursor.execute('create table {0} (id serial primary key, subject_id {1} not null, match_id {2}, confidence numeric not null)'.format(table, self.subject_id_type, self.match_id_type))
                transaction.commit()
            except DatabaseError:
                transaction.rollback()
                raise CommandError('Database table exists. Wait a minute and try again.')

        try:
            for i, subject in enumerate(self.subject.all()[begin_at-1:]):
                log_msg = ''

                print u"{0}/{1}: {2}".format(begin_at+i, count, getattr(subject, self.subject_name_attr))
                #pre-process subject name
                subject_raw_name = self.preprocess_subject_name(getattr(subject, self.subject_name_attr))

                try:
                    subject_name = self.name_cleaver(subject_raw_name).parse()

                    if self.name_processing_failed(subject_name):
                        continue
                except:
                    continue
                finally:
                    transaction.rollback()

                # search match entities
                potential_matches = self.get_potential_matches_for_subject(subject_name, subject)
                log_msg += 'Potential matches: {0}; '.format(potential_matches.count())

                matches_we_like = {}
                for match in potential_matches:
                    match_name = self.name_cleaver(getattr(match, self.match_name_attr)).parse()

                    if isinstance(match_name, RunningMatesNames):
                        for running_mate_name in match_name.mates():
                            confidence = self.get_confidence(running_mate_name, subject_name)
                    else:
                        confidence = self.get_confidence(match_name, subject_name)

                    if confidence >= self.confidence_threshold:
                        if not matches_we_like.has_key(confidence):
                            matches_we_like[confidence] = []

                        matches_we_like[confidence].append(match)

                confidence_levels = matches_we_like.keys()
                if len(confidence_levels):
                    confidence_levels.sort()

                    for match in matches_we_like[confidence_levels[-1]]:
                        self.insert_match(cursor, table, match, subject, confidence_levels[-1])

                        if options['do_post_insert']:
                            self.post_insert()

                        transaction.commit()
                        log_msg += 'Committed.'

                elif options['insert_non_matches']:
                    # a confidence of -1 means no matches were found
                    self.insert_match(cursor, table, None, subject, -1)
                    transaction.commit()
                    log_msg += 'Committed no-match.'

                print log_msg
                sys.stdout.flush()


        except KeyboardInterrupt:
            transaction.commit()
            print '\nTo resume, run:'
            print './manage.py {0} -b {1} -t {2}'.format(self.__module__.split('.')[-1], begin_at+i, table)

        print 'Done. Find your results in {0}.'.format(table)


    def name_processing_failed(self, subject_name):
        return isinstance(subject_name, RunningMatesNames) or not subject_name.last


    def preprocess_subject_name(self, name):
        return name


    def get_potential_matches_for_subject(self, subject_name, subject_obj):
        """
            Takes a name cleaver object and ideally returns a loosely matched set of objects
            which we can then filter more stringently by scoring
        """

        key = subject_name.last.encode('utf-8')
        key = re.sub(r'[^-a-zA-Z0-9,.\'"^&*()]', '', key)
        key = key.lower()
        obj = self.mc.get(key)
        if not obj:
            obj = self.match.filter(**{'{0}__{1}'.format(self.match_name_attr, self.match_operator): subject_name.last})
            self.mc.set(key, obj)

        return obj


    def do_after_insert(self, subject, match, confidence):
        pass


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
        # matches can be null if we are putting in a no-confidence record for no potential matches found
        if match:
            cursor.execute("insert into {0} (subject_id, match_id, confidence) values ('{1}', '{2}', {3})".format(table_name, subject.pk, match.pk, confidence))
        else:
            cursor.execute("insert into {0} (subject_id, confidence) values ('{1}', {2})".format(table_name, subject.pk, confidence))


    def generate_table_name(self):
        date_time_now = datetime.datetime.now().strftime('%Y%m%d_%H%M')
        return '_'.join([self.match_table_prefix, 'matches', date_time_now])



