from django.core.management import BaseCommand, CommandError
import csv, os
from dcentity.models import Entity
from name_cleaver import *
from django.template import Template, Context
from django.db import connection
from optparse import make_option

question_xml = """<?xml version="1.0" encoding="UTF-8"?>
<QuestionForm xmlns="http://mechanicalturk.amazonaws.com/AWSMechanicalTurkDataSchemas/2005-10-01/QuestionForm.xsd">
    <Overview>
        <Text>
            We have a database of entities related to United States campaign finance (politicians, organizations, individual campaign contributors, lobbyists, etc.).  We have attempted to match these entities to corresponding descriptions of them via an automated process.  Your task is to determine whether or not the Wikipedia match was successful.  You will be supplied with a list of known-accurate metadata (varies by organization, but may include name, office held, party, etc.), along with a sample from the description.  If the description and the metadata appear to describe the same person, answer "yes;" if they clearly do not, answer "no."  If there is insufficient information to determine whether or not they are the same, answer "unclear."
        </Text>
    </Overview>
    <Question>
        <QuestionIdentifier>is_match</QuestionIdentifier>
        <DisplayName>Do this metadata and this description describe the same entity?</DisplayName>
        <QuestionContent>
            <FormattedContent><![CDATA[
                <h2>Metadata</h2>
                ${metadata}
                <hr />
                <h2>Wikipedia Description</h2>
                ${wikipedia_bio}
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
"""

properties = """
######################################
##  HIT Properties
######################################

title:Wikipedia match validation
description:We have matched a set of entities in a database to descriptions pulled from Wikipedia via an automated process. Confirm that the match is correct.
keywords:movie, survey
reward:0.08
assignments:3
annotation:wikipedia_match

######################################
## HIT Timing Properties
######################################

# this Assignment Duration value is 60 * 60 = 1 hour
assignmentduration:3600

# this HIT Lifetime value is 60*60*24*7 = 7 days
hitlifetime:604800

# this Auto Approval period is 60*60*24*5 = 5 days
autoapprovaldelay:432000
"""

metadata_template = Template("""{% spaceless %}
<strong>Name:</strong> {{ standard_name }}<br />
<strong>Type:</strong> {{ entity.type|capfirst }}<br />

{% if entity.type == 'politician' %}
<strong>Party:</strong> {{ entity.metadata.party }}<br />

{% if entity.metadata.seat %}
<strong>Last office sought:</strong> {% if entity.metadata.state %}{{ entity.metadata.state }} {% endif %}{{ entity.metadata.seat }}<br />
{% endif %}
{% if metadata.seat_held %}
<strong> Last office held:</strong> {% if entity.metadata.state_held %}{{ entity.metadata.state_held }} {% endif %}{{ metadata.seat_held }}<br />
{% endif %}

{% endif %}

{% if entity.type == 'organization' %}
<strong>Is Lobbying Firm:</strong> {% if entity.organization_metadata.lobbying_firm %}Yes{% else %}No{% endif %}<br />
<strong>Industry:</strong> {{ entity.organization_metadata.industry_entity|lower|capfirst }}<br />
{% endif %}
{% endspaceless %}""")

wikipedia_bio_template = Template("""{% spaceless %}
<strong>From Wikipedia Page <a href="{{ entity.metadata.bio_url }}">{{ entity.metadata.bio_url }}</a>:</strong><br /><br />

{{ entity.metadata.bio|safe }}
{% endspaceless %}""")

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

def get_row(id):
    entity = Entity.objects.get(id=id)
    
    standard_name = standardizers[entity.type](entity.name).parse().__str__()
    
    # make fields pretty
    print entity.id, entity.type
    
    for key in ['seat', 'seat_held', 'party']:
        if key in entity.metadata and entity.metadata[key] in substitutions:
            entity.metadata[key] = substitutions[entity.metadata[key]]
    
    context = Context({'standard_name': standard_name, 'entity': entity})
    
    return {
        'id': entity.id,
        'name': standard_name,
        'type': entity.type,
        'metadata': metadata_template.render(context).encode('utf-8'),
        'wikipedia_bio': wikipedia_bio_template.render(context).encode('utf-8'),
    }

def ensure_directory(dir):
    if not (os.path.exists(dir) and os.path.isdir(dir)):
        os.mkdir(dir)

class Command(BaseCommand):
    args = '<directory>'
    help = 'Collapses files into one directory'
    option_list = BaseCommand.option_list + (
        make_option('-n', '--number',
            action='store',
            dest='count',
            default=1000,
            help='Number of tasks to create.'),
    )
    
    def handle(self, *args, **options):
        if len(args) != 1:
            raise CommandError('Please specify a directory.')
        
        directory = args[0]
        
        # check that directories exists
        ensure_directory(directory)
        os.chdir(directory)
        
        # output plain files first
        xml_file = open('wikipedia_matches.question', 'w')
        xml_file.write(question_xml)
        xml_file.close()
        
        props_file = open('wikipedia_matches.properties', 'w')
        props_file.write(properties)
        props_file.close()
        
        # output CSV
        csv_file = open('wikipedia_matches.input', 'wb')
        csv_writer = csv.DictWriter(csv_file, ['id', 'name', 'type', 'metadata', 'wikipedia_bio'], delimiter="\t")
        csv_writer.writeheader()
        
        # get rows and generate metadata text
        cursor = connection.cursor()
        cursor.execute("""
        select entity_id from matchbox_wikipediainfo where entity_id not in (select entity_id from matchbox_sunlightinfo) and bio != '' and bio is not null order by entity_id limit %s;
        """,
        [options['count']])
        
        for row in cursor:
            csv_writer.writerow(get_row(row[0]))
        
        csv_file.close()