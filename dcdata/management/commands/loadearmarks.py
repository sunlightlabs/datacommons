
from dcdata.earmarks.models import Member, Earmark, Location, presidential_raw, \
    undisclosed_raw
from dcdata.models import Import
from dcdata.processor import chain_filters, load_data, SkipRecordException, \
    TerminateProcessingException
from dcdata.utils.dryrub import CSVFieldVerifier, VerifiedCSVSource
from decimal import Decimal, InvalidOperation
from django.core.management.base import BaseCommand
from django.db.utils import DatabaseError
from saucebrush.filters import FieldAdder, FieldMerger, FieldRemover, \
    FieldModifier
from sys import stderr

FIELDS = [
    'id',
    'house_amount',
    'senate_amount',
    'omni_amount',
    'final_amount',
    'budget_amount',
    'description',
    'city',
    'county',
    'state',
    'bill',
    'bill_section',
    'bill_subsection',
    'project_heading',
    'house_members',
    'house_parties',
    'house_states',
    'house_districts',
    'senate_members',
    'senate_parties',
    'senate_states',
    'presidential',
    'undisclosed',
    'raw_recipient',
    'notes'
]

def _warn(message):
    stderr.write("WARNING: %s\n" % message)


def district_filter(value):
    try:
        value = value.replace('st', '').replace('nd', '').replace('rd', '').replace('th', '')
        return int(value) if value else 0
    except ValueError:
        _warn("Could not parse district: %s" % value)


def amount_filter(value):
    value = value.strip().replace('$', '').replace(',', '')
    
    if value == '' or value in ('(see note)', 'Intel (No Numbers)'):
        return Decimal(0)
    
    try:
        return Decimal(value)
    except InvalidOperation:
        _warn("Could not parse amount: %s" % value)
        return Decimal(0)


def string_filter(s, max_length):
    if len(s) > max_length:
        _warn("Truncating string: %s" % s[:max_length])
        
    return s[:max_length]

def state_filter(state_string):
    if len(state_string) == 0 or len(state_string) ==2:
        return state_string
    
    if state_string not in ('UNK', 'INT', 'Int', 'UST', 'N/A', 'I', 'National', 'USVI', 'Multi'):
        # we know we're ignoring these; others are worth a warning
        _warn("Dropping unknown state: %s" % state_string)
    return ''

def party_filter(party_string):
    if party_string.upper()  in ('', 'D', 'R', 'I'):
        return party_string.upper()
    
    if party_string not in ('N/A'):
        _warn("Dropping unknown party: %s" % party_string)
    return ''



def _prepend(prefix, suffix):
    return "%s -- %s" % (prefix, suffix) if prefix else suffix


def split_and_transpose(separator, *strings):
    """ 
        Go from a list like ('Bob; Jeff', 'D; R', 'CA; VA') to [('Bob', 'D', 'CA'), ('Jeff', 'R', 'VA')] 
    """
    
    # all empty strings returns empty list
    if not any(strings):
        return []

    splits = [[value.strip() for value in s.split(separator)] if s else [] for s in strings]
            

    if len(splits) == 1:
        return [(s,) for s in splits[0]]
    else:
        splits = [s if len(s) == len(splits[0]) else [''] * len(splits[0]) for s in splits]
        return map(None, *splits)


def _normalize_locations(city_string, state_string):
    
    def create_location(city, state):
        return Location(city=city, state=state)
    
    cities = [city.strip() for city in city_string.split(';')] if city_string else []
    states = [state_filter(state.strip()) for state in state_string.split(';')] if state_string else []
    
    # if they're all empty strings then return nothing
    if not any(cities) and not any(states):
        return []
    
    # allow city/state pairs
    if len(cities) == len(states):
        return map(create_location, cities, states)
    
    # allow only cities
    if len(states) == 0:
        return map(create_location, cities, [''] * len(cities))
    
    # allow only states
    if len(cities) == 0:
        return map(create_location, [''] * len(states), states)
    
    # allow multiple cities in single state
    if len(states) == 1:
        return map(create_location, cities, states * len(cities))
    
    # when multiple states and a different number of cities, don't make any associations
    return map(create_location, cities, [''] * len(cities)) + map(create_location, [''] * len(states), states)


def _normalize_chamber(chamber, names, parties, states, districts=None):
    
    def create_member(values):
        district = district_filter(values[3]) if len(values) == 4 else None
        state = state_filter(values[2])
        party = party_filter(values[1])
        
        return Member(chamber=chamber, raw_name=values[0], party=party, state=state, district=district)
    
    if districts:
        split = split_and_transpose(';', names, parties, states, districts)
    else:
        split = split_and_transpose(';', names, parties, states)
    
    
    return map(create_member, split)


def _normalize_members(house_names, house_parties, house_states, house_districts, senate_names, senate_parties, senate_states):
    return _normalize_chamber('h', house_names, house_parties, house_states, house_districts) + \
        _normalize_chamber('s', senate_names, senate_parties, senate_states)
 

def save_earmark(earmark_dict):   
    try:
        members = earmark_dict.pop('members', [])
        locations = earmark_dict.pop('locations', [])
        e = Earmark.objects.create(**earmark_dict)
        e.members = members
        e.locations = locations
    except DatabaseError as e:
        raise TerminateProcessingException(e)

class LoadTCSEarmarks(BaseCommand):
    
    @staticmethod
    def get_record_processor(year, import_ref):
        return chain_filters(
            CSVFieldVerifier(),

            FieldRemover('id'),
            FieldRemover('county'),

            FieldAdder('fiscal_year', year),
            FieldAdder('import_reference', import_ref),
            
            FieldModifier(['notes'], lambda s: string_filter(s, 1024)),
            FieldModifier(['description', 'house_members', 'senate_members'], lambda s: string_filter(s, 512)),
            FieldModifier(['bill_section', 'bill_subsection', 'raw_recipient', 'house_parties', 'house_states', 'house_districts', 'senate_parties', 'senate_states'],
                           lambda s: string_filter(s, 256)),
            
            FieldModifier(['budget_amount', 'senate_amount', 'house_amount', 'omni_amount', 'final_amount'], amount_filter),
                        
            FieldMerger({'description': ('project_heading', 'description')}, _prepend),

            FieldModifier(['presidential'], lambda p: presidential_raw.get(p, '')),
            FieldModifier(['undisclosed'], lambda u: undisclosed_raw.get(u, '')),

            FieldMerger({'locations': ('city', 'state')}, _normalize_locations),
            FieldMerger({'members': ('house_members', 'house_parties', 'house_states', 'house_districts',
                                        'senate_members', 'senate_parties', 'senate_states')},
                            _normalize_members, keep_fields=True),
        )    
    
    def handle(self, input_path, year, **options):
        imp = Import.objects.create(source=input_path, imported_by=__file__)
        
        input_file = open(input_path, 'r')
        
        input_source = VerifiedCSVSource(input_file, FIELDS, skiprows=1)
        processor = LoadTCSEarmarks.get_record_processor(int(year), imp) # todo: real year and import_ref
        
        load_data(input_source, processor, save_earmark)

Command = LoadTCSEarmarks