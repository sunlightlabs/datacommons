from dcentity.models             import Entity
from django.core.management.base import CommandError, BaseCommand
from django.db                   import connections, transaction
from guidestar.models            import Officer
from name_cleaver.name_cleaver   import PoliticianNameCleaver, RunningMatesNames, PoliticianName
from optparse                    import make_option

import datetime, re

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option("-b", "--begin_at_count", dest="begin_at_count", help="Number to resume script at", metavar="INTEGER"),
    )

    @transaction.commit_manually
    def handle(self, *args, **options):
        count = Officer.objects.count()
        begin_at = int(options.get('begin_at_count', 0))

        date_time_now = datetime.datetime.now().strftime('%Y%m%d_%H%M')
        match_table_name = 'guidestar_matches_{0}'.format(date_time_now)

        print 'Creating {0}'.format(match_table_name)
        cursor = connections['default'].cursor()
        cursor.execute('create table {0} (id serial primary key, subject_id uuid not null, match_id uuid not null, confidence numeric not null)'.format(match_table_name))
        transaction.commit()

        for i, officer in enumerate(Officer.objects.all()[begin_at-1:]):

            print "{0}/{1}: {2}".format(begin_at+i, count, officer.name)
            officer_raw_name = officer.name
            officer_raw_name = re.sub(r' CBO$', '', officer_raw_name)
            officer_raw_name = re.sub(r' PE C$', '', officer_raw_name)
            officer_raw_name = re.sub(r' M$', '', officer_raw_name)
            officer_raw_name = re.sub(r', M\.?D\.?$', '', officer_raw_name)

            # search politician entities
            officer_name = PoliticianNameCleaver(officer_raw_name).parse()

            if isinstance(officer_name, RunningMatesNames) or not officer_name.last:
                continue

            potential_politician_matches = Entity.objects.filter(type='politician').filter(name__icontains=officer_name.last)
            print 'Potential matches: {0}'.format(potential_politician_matches.count())

            for pol in potential_politician_matches:
                pol_name = PoliticianNameCleaver(pol.name).parse()

                if isinstance(pol_name, RunningMatesNames):
                    for running_mate_name in pol_name.mates():
                        confidence = self.get_confidence(running_mate_name, officer_name)
                else:
                    confidence = self.get_confidence(pol_name, officer_name)

                if confidence >= 2:
                    self.insert_match(cursor, match_table_name, pol, officer, confidence)

                # match state
                # pol.metadata_for_latest_cycle.state

#            if i > 101:
#                break

    def get_confidence(self, pol_name, officer_name):
        return officer_name.score_match(pol_name)


    def insert_match(self, cursor, table_name, pol, officer, confidence):
        print 'Inserting.'
        cursor.execute("insert into {0} (subject_id, match_id, confidence) values ('{1}', '{2}', {3})".format(table_name, officer.id, pol.id, confidence))
        transaction.commit()




