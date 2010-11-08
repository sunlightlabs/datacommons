
from django.core.management.base import BaseCommand
from saucebrush.filters import FieldAdder, FieldMerger, FieldRemover,\
    FieldRenamer, FieldModifier
from dcdata.utils.dryrub import CSVFieldVerifier, VerifiedCSVSource
from dcdata.earmarks.models import Member, Earmark, Location, presidential_raw, undisclosed_raw
from dcdata.processor import chain_filters, load_data


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


def fill_missing_zeros(value):
    return value if value else 0


def _prepend(prefix, suffix):
    return "%s -- %s" % (prefix, suffix) if prefix else suffix


def split_and_transpose(separator, *strings):
    """ 
        Go from a list like ('Bob; Jeff', 'D; R', 'CA; VA') to [('Bob', 'D', 'CA'), ('Jeff', 'R', 'VA')] 

        Raises an error if the lists don't all have same number of elements.
    """
    
    # all empty strings returns empty list
    if not any(strings):
        return []

    splits = [[value.strip() for value in s.split(separator)] for s in strings]

    if not all([len(split) == len(splits[0]) for split in splits]):
        raise

    return map(None, *splits)


def _normalize_locations(city_string, state_string):
    
    def create_location(city, state):
        return Location(city=city, state=state)
    
    cities = [city.strip() for city in city_string.split(';')]
    states = [state.strip() for state in state_string.split(';')]
    states = ['' if state == 'UNK' else state for state in states]
    
    # if they're all empty strings then return nothing
    if not any(cities) and not any(states):
        return []
    
    # allow city/state pairs
    if len(cities) == len(states):
        return map(create_location, cities, states)
    
    # allow only cities
    if len(states) == 0:
        return map(create_location, cities, '' * len(cities))
    
    # allow only states
    if len(cities) == 0:
        return map(create_location, '' * len(states), states)
    
    # allow multiple cities in single state
    if len(states) == 1:
        return map(create_location, cities, states * len(cities))
    
    # from here there must be multiple states and a different number of cities
    print "WARNING: dropping cities from ambiguous location: '%s', '%s" % (city_string, state_string)
    return []


def _normalize_chamber(chamber, names, parties, states, districts=None):
    
    def create_member(values):
        return Member(chamber=chamber, raw_name=values[0], party=values[1], state=values[2], district=values[3] if len(values)==4 else None)
    
    if districts:
        split = split_and_transpose(';', names, parties, states, districts)
    else:
        split = split_and_transpose(';', names, parties, states)
    
    
    return map(create_member, split)


def _normalize_members(house_names, house_parties, house_states, house_districts, senate_names, senate_parties, senate_states):
    return _normalize_chamber('h', house_names, house_parties, house_states, house_districts) + \
        _normalize_chamber('s', senate_names, senate_parties, senate_states)


def _presidential_filter(presidential_raw):
    return 
    


def save_earmark(earmark_dict):   
    members = earmark_dict.pop('members', [])
    locations = earmark_dict.pop('locations', [])
    e = Earmark.objects.create(**earmark_dict)
    e.members = members
    e.locations = locations


class LoadTCSEarmarks(BaseCommand):
    
    @staticmethod
    def get_record_processor(year, import_ref):
        return chain_filters(
            CSVFieldVerifier(),

            FieldRemover('id'),
            FieldRemover('county'),

            FieldAdder('fiscal_year', year),
            FieldAdder('import_reference', import_ref),
            
            FieldModifier(['budget_amount', 'senate_amount', 'house_amount', 'omni_amount', 'final_amount'], fill_missing_zeros),
            
            FieldMerger({'description': ('project_heading', 'description')}, _prepend),

            FieldModifier(['presidential'], lambda p: presidential_raw.get(p, '')),
            FieldModifier(['undisclosed'], lambda u: undisclosed_raw.get(u, '')),

            FieldMerger({'locations': ('city', 'state')}, _normalize_locations),
            FieldMerger({'members': ('house_members', 'house_parties', 'house_states', 'house_districts',
                                        'senate_members', 'senate_parties', 'senate_states')},
                            _normalize_members),
        )    
    
    def handle(self, input_path, **options):
        input_file = open(input_path, 'r')
        
        input_source = VerifiedCSVSource(input_file, FIELDS, skiprows=1)
        processor = LoadTCSEarmarks.get_record_processor(0, None) # todo: real year and import_ref
        
        load_data(input_source, processor, save_earmark)
