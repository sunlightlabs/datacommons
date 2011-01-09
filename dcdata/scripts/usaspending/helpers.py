from django.contrib.localflavor.us.us_states import STATES_NORMALIZED
import datetime

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
        return ''

def state_abbr(value):
    return STATES_NORMALIZED.get(value.strip().lower(), '')


def agency_name_lookup(value):
    agencies = {}
    # NOTE: I don't know where this agencies lookup file is. This should not be hardcoded
    # but come from a file. I don't see any candidates for it in the repo. :(
    return agencies.get(value, '')

def datestamp():
    return datetime.datetime.strftime(datetime.datetime.today(), '%Y%m%d')

