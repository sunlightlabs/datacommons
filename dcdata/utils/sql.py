
from datetime import datetime, date
from time import strptime
from decimal import Decimal



def null_check(func):
    return (lambda x: None if x == '\\N' else func(x))

def _parse_int(int_str):
     if not int_str or int_str == '\\N':
         return None

     return int(int_str)

def _parse_date(date_str):
    if not date_str or date_str == "0000-00-00":
        return None

    return date(*(strptime(date_str, "%Y-%m-%d")[0:3]))

def _parse_datetime(datetime_str):
    if not datetime_str or datetime_str == "0000-00-00 00:00:00":
        return None

    return datetime(*(strptime(datetime_str, "%Y-%m-%d %H:%M:%S")[0:6]))

parse_float = null_check(float)
parse_int = null_check(_parse_int)
parse_date = null_check(_parse_date)
parse_datetime = null_check(_parse_datetime)
parse_char = null_check(lambda x: None if x == 'XXX' else x)
parse_decimal = null_check(Decimal)
parse_int_id = null_check(lambda x: None if x == '0' else _parse_int(x))




def augment(initial_dict, **new_items):
    """ Return a new dictionary that contains the items from initial_dict with new_items added on top. """

    result = dict(initial_dict)
    for (key, value) in new_items.items():
        result[key] = value
    return result


def dict_union(*dictionaries):
    """ Return the union of the given dictionaries. Undefined behavior for repeat keys. """
    result = dict()
    for d in dictionaries:
        result.update(d)
    return result



