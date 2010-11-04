
from django.core.management.base import CommandError, BaseCommand
from saucebrush.filters import FieldAdder, FieldMerger, FieldRemover, Filter
from dcdata.utils.dryrub import FieldCountValidator, CSVFieldVerifier, VerifiedCSVSource
from dcdata.earmarks.models import Earmark, Member
from dcdata.processor import chain_filters


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
    'recipient',
    'notes'
]

def _prepend(prefix, suffix):
    return "%s -- %s" % (prefix, suffix) if prefix else suffix


def split_and_transpose(separator, *strings):
    """ 
        Go from a list like ('Bob; Jeff', 'D; R', 'CA; VA') to [('Bob', 'D', 'CA'), ('Jeff', 'R', 'VA')] 

        Raises an error if the lists don't all have same number of elements.
    """

    splits = [[value.strip() for value in s.split(separator)] for s in strings]
    #splits = map(lambda s: map(str.strip, s.split(c)), strings)

    if not all([len(split) == len(splits[0]) for split in splits]):
        raise

    return map(None, *splits)


def _normalize_chamber(chamber, names, parties, states, districts=None):
    
    def create_member(values):
        return Member(chamber=values[0], raw_name=values[1], party=values[2], state=values[3], district=values[4] if len(values)==4 else None)
    
    if districts:
        split = split_and_transpose(';', names, parties, states, districts)
    else:
        split = split_and_transpose(';', names, parties, states)
    
    return map(create_member, split)


def _normalize_members(house_names, house_parties, house_states, house_districts, senate_names, senate_parties, senate_states):
    return _normalize_chamber('h', house_names, house_parties, house_states, house_districts) + \
        _normalize_chamber('s', senate_names, senate_parties, senate_states)



class LoadTCSEarmarks(BaseCommand):
    
    @staticmethod
    def get_record_processor(year, import_ref):
        return chain_filters(
            CSVFieldVerifier(),

            FieldRemover('id'),
            FieldMerger({'description': ('project_heading', 'description')}, _prepend),
            FieldAdder('fiscal_year', year),
            FieldAdder('import_reference', import_ref),

            FieldMerger({'members': ('house_members', 'house_parties', 'house_states', 'house_districts',
                                        'senate_members', 'senate_parties', 'senate_states')},
                            _normalize_members),
        )    
    
    def handle(self, input_path, **options):
        input_file = open(input_path, 'r')
        
        input_source = VerifiedCSVSource(input_file, FIELDS, skiprows=1)

