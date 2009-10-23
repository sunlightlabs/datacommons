
def django2sql_names(model):
    """ Return a dictionary from Django model field names to SQL column names, plus the model class name to table name. """
    
    result = dict()
    result[model.__name__.lower()] = model._meta.db_table   
    
    fields = [field_name for (field_name, model) in model._meta.get_fields_with_model() if not model]
    for field in fields:
        result[field.name.lower()] = field.column
        
    return result