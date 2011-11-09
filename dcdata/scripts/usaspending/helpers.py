from django.contrib.localflavor.us.us_states import STATES_NORMALIZED
import datetime


def correctionLateIndicator(value):
    
    if value == 'current entry':
        return ''
    elif value[0] == 'C':
        return 'C'
    elif value[0] == 'L':
        return 'L'
    
    return ''
    

def nullable(value):
    if value == '':
        return None
    
    return value

def nullable_float(value):
    if value == '' or value == 'N/A':
        return None
    
    return float(value)

def nullable_int(value):
    if value == '':
        return None
    
    parsed_value = int(value)
    
    # these are Postgres' limits
    if parsed_value < -2147483648 or parsed_value > 2147483647:
        return None
    
    return parsed_value


def splitInt(value):

    if not value is None:
        return int(value.split('.')[0])
    else:
        return None

def splitIntCode(value):

    code = splitCode(value)

    if not code == '':
        return int(code)
    else:
        return None

def splitCode(value):

    if not value is None:
        return value.split(':')[0]
    else:
        return ''

def transformFlag(value):

    if value and value[0]:
        if value[0].lower() in ('y', 't'):
            return 't'
        elif value[0].lower() in ('n', 'f'):
            return 'f'
    else:
        return None

def first_char(value):
    return value[:1]

def recovery_act(value):
    if value:
        if value.lower() in ("recovery act", 'y', 't'):
            return 't'
        elif value.lower() in ('n', 'f'):
            return 'f'
    
    return None


def state_abbr(value):
    return STATES_NORMALIZED.get(value.strip().lower(), '')


def agency_name_lookup(value):
    agencies = {}
    # NOTE: I don't know where this agencies lookup file is. This should not be hardcoded
    # but come from a file. I don't see any candidates for it in the repo. :(
    return agencies.get(value, '')

def datestamp():
    return datetime.datetime.strftime(datetime.datetime.today(), '%Y%m%d')

