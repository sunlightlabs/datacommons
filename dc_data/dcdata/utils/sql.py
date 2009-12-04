
from datetime import datetime


def null_check(func):
    return (lambda x: None if x == '\\N' else func(x))

def _parse_date(date_str):
    if date_str == "0000-00-00":
        return None
    
    return datetime.strptime(date_str, "%Y-%m-%d")

def _parse_datetime(datetime_str):
    if datetime_str == "0000-00-00 00:00:00":
        return None

    return datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")

parse_float = null_check(float)
parse_int = null_check(int)
parse_date = null_check(_parse_date)
parse_datetime = null_check(_parse_datetime)
parse_char = null_check(lambda x: x)



def django2sql_names(model):
    """ Return a dictionary from Django model field names to SQL column names, plus the model class name to table name. """
    
    result = dict()
    model_name = model.__name__.lower()
    result[model_name] = model._meta.db_table   
    
    fields = [field_name for (field_name, model) in model._meta.get_fields_with_model() if not model]
    for field in fields:
        result[model_name + "_" + field.name.lower()] = field.column
        
    return result



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
    
    
def is_disjoint(*iterables):
    """ 
    Return true iff all sets are pairwise disjoint. 
    
    If arguments are dictionaries then just use the keys.
    """
    already_seen = set()
    for i in iterables:
        for x in i:
            if x in already_seen:
                return False
            already_seen.add(x)
    return True

