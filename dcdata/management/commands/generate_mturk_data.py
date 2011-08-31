from django.core.management import BaseCommand, CommandError
import csv, os
from dcentity.models import Entity
from name_cleaver import *
from django.template import Template, Context
from django.db import connection
from optparse import make_option
from boto.mturk.question import QuestionForm
from boto.mturk.connection import MTurkConnection
from boto.mturk.qualification import Qualifications, PercentAssignmentsApprovedRequirement
import datetime, sys, re
from django.conf import settings

question_template = Template("""<?xml version="1.0" encoding="UTF-8"?>
<QuestionForm xmlns="http://mechanicalturk.amazonaws.com/AWSMechanicalTurkDataSchemas/2005-10-01/QuestionForm.xsd">
    <Overview>
        <Text>
            We have a database of entities related to United States campaign finance (politicians, companies and organizations). We have attempted to match these entities to corresponding descriptions of them via an automated process. Your task is to determine whether or not the Wikipedia bio is a description of the politician or organization. You will be supplied with a list of known-accurate metadata (varies by entity, but may include name, office held, party, etc.), along with a sample from the description. If the description and the metadata appear to describe the same person or organization, answer "yes;" if they clearly do not, answer "no." If there is insufficient information to determine whether or not they are the same, answer "unclear."
        </Text>
    </Overview>
    <Question>
        <QuestionIdentifier>is_match</QuestionIdentifier>
        <DisplayName>Do this metadata and this description describe the same entity?</DisplayName>
        <QuestionContent>
            <FormattedContent><![CDATA[
                <h2>Metadata</h2>
                {% spaceless %}
                <strong>Name:</strong> {{ standard_name }}<br />
                <strong>Type:</strong> {{ entity.type|capfirst }}<br />
                
                {% if entity.type == 'politician' %}
                <strong>Party:</strong> {{ metadata.party }}<br />
                
                {% if metadata.seat %}
                <strong>Last office sought:</strong> {% if metadata.state %}{{ metadata.state }} {% endif %}{{ metadata.seat }}<br />
                {% endif %}
                {% if metadata.seat_held %}
                    {% if metadata.seat_held == "US House" and metadata.district_held == "-" %}{% else %}
                    <strong> Last office held:</strong> {% if metadata.state_held %}{{ metadata.state_held }} {% endif %}{{ metadata.seat_held }}<br />
                    {% endif %}
                {% endif %}
                
                {% endif %}
                
                {% if entity.type == 'organization' %}
                <strong>Is Lobbying Firm:</strong> {% if entity.organization_metadata.lobbying_firm %}Yes{% else %}No{% endif %}<br />
                <strong>Industry:</strong> {{ entity.organization_metadata.industry_entity|lower|capfirst }}<br />
                {% endif %}
                {% endspaceless %}
                <hr />
                
                <h2>Wikipedia Description</h2>
                {% spaceless %}
                <strong>From Wikipedia Page <a href="{{ metadata.bio_url }}">{{ metadata.bio_url }}</a>:</strong><br /><br />
                
                {{ metadata.bio|safe }}
                {% endspaceless %}
            ]]></FormattedContent>
        </QuestionContent>
        <AnswerSpecification>
            <SelectionAnswer>
                <StyleSuggestion>radiobutton</StyleSuggestion>
                <Selections>
                    <Selection>
                        <SelectionIdentifier>yes</SelectionIdentifier>
                        <Text>Yes, this description matches the entity in question.</Text>
                    </Selection>
                    <Selection>
                        <SelectionIdentifier>no</SelectionIdentifier>
                        <Text>No, this description does not match the entity in question.</Text>
                    </Selection>
                    <Selection>
                        <SelectionIdentifier>maybe</SelectionIdentifier>
                        <Text>Unclear; there is insufficient information to determine whether or not the description matches this entity.</Text>
                    </Selection>
                </Selections>
            </SelectionAnswer>
        </AnswerSpecification>
    </Question>
</QuestionForm>
""")

standardizers = {
    'individual': IndividualNameCleaver,
    'organization': OrganizationNameCleaver,
    'politician': PoliticianNameCleaver
}

substitutions = {
    'federal:senate': 'US Senate',
    'federal:house': 'US House',
    'federal:president': 'President',
    'state:upper': 'State Upper Chamber',
    'state:lower': 'State Lower Chamber',
    'state:governor': 'Governor',
    'state:ltgovernor': 'Lt. Governor',
    'state:judicial': 'State Judiciary',
    'state:office': 'Other State Office',
    'D': 'Democrat',
    'R': 'Republican',
    'I': 'Independent'
}

ampersand_fix = re.compile(r'&([\w.,]*\s)')

def get_hit_xml(id):
    entity = Entity.objects.get(id=id)
    
    standard_name = standardizers[entity.type](entity.name).parse().__str__()
    
    # make fields pretty
    metadata = entity.metadata
    for key in ['seat', 'seat_held', 'party']:
        if key in metadata and metadata[key] in substitutions:
            metadata[key] = substitutions[metadata[key]]
    
    metadata['bio'] = ampersand_fix.sub(lambda m: '&amp;%s' % m.group(1), metadata['bio'])
    
    context = Context({'standard_name': standard_name, 'entity': entity, 'metadata': metadata})
    
    return question_template.render(context).encode('utf-8')

class FakeQuestionForm(QuestionForm):
    def __init__(self, xml):
        self.full_xml = xml
    
    def is_valid(self):
        return True
    
    def get_as_xml(self):
        return self.full_xml
    
    # hack to make it boolean-ize correctly
    def __nonzero__(self):
        return True

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-n', '--number',
            action='store',
            dest='count',
            default=100000,
            help='Number of tasks to create.'),
        make_option('-d', '--delete',
            action='store_true',
            dest='delete_first',
            default=False,
            help='Delete all old records before creating new ones.'),
        make_option('-s', '--sandbox',
            action='store_true',
            dest='sandbox',
            default=False,
            help='Use the sandbox server instead of the production one.'),
        make_option('-p', '--practice',
            action='store_true',
            dest='practice',
            default=False,
            help='Print matched IDs to the screen instead of submitting anything.'),
        make_option('-x', '--exclude',
            action='store',
            dest='exclude',
            default=None,
            help='CSV file containing a td_id column of already completed IDs not to submit on this batch.'),
        make_option('-t', '--type',
            action='store',
            dest='type',
            default=None,
            help='Restrict submissions to a single type.')
    )
    
    def handle(self, *args, **options):
        # create a connection
        mturk = MTurkConnection(
            getattr(settings, 'MTURK_AWS_KEY', settings.MEDIASYNC['AWS_KEY']),
            getattr(settings, 'MTURK_AWS_SECRET', settings.MEDIASYNC['AWS_SECRET']),
            host = 'mechanicalturk.sandbox.amazonaws.com' if options['sandbox'] else 'mechanicalturk.amazonaws.com'
        )
        
        # if --delete, delete all the old ones first.
        if options['delete_first']:
            for hit in mturk.get_all_hits():
                mturk.disable_hit(hit.HITId)
        
        if options['exclude']:
            exclude_reader = csv.DictReader(open(options['exclude'], 'r'))
            exclude = set()
            for row in exclude_reader:
                exclude.add(row['td_id'])
        
        # iterate over items and create them one by one
        cursor = connection.cursor()
        cursor.execute(
            """
            select entity_id, type from matchbox_wikipediainfo, matchbox_entity where entity_id not in (select entity_id from matchbox_sunlightinfo where bio is not null) and bio != '' and bio is not null and entity_id = matchbox_entity.id %s order by entity_id limit %s;
            """ % ("and type = '%s'" % options['type'] if options['type'] else '', '%s'), # hack to put the interpolation string back in for PG to catch it
        [options['count']])
        
        for row in cursor:
            if options['exclude']:
                if str(row[0]).replace('-', '') in exclude:
                    continue
            
            if options['practice']:
                print row[0]
                continue
            
            try:
                hit = mturk.create_hit(
                    question = FakeQuestionForm(get_hit_xml(row[0])),
                    max_assignments = 3,
                    annotation = row[0],
                    
                    title = "Wikipedia match validation",
                    description = "We have matched a set of entities in a database to descriptions pulled from Wikipedia via an automated process. Confirm that the match is correct.",
                    reward = 0.07,
                    duration = datetime.timedelta(days=7),
                    keywords = ['wikipedia', 'matching'],
                    approval_delay = datetime.timedelta(days=3),
                    qualifications = Qualifications([PercentAssignmentsApprovedRequirement("GreaterThan", 90)])
                )
                print hit[0].HITId
            except Exception as e:
                sys.stderr.write("Failed to create hit %s\n" % row[0])
                sys.stderr.write(getattr(e, 'body', ''))
                sys.stderr.write('\n')
            except:
                pass
