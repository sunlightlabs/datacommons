
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
