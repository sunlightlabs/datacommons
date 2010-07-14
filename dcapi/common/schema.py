from dcdata.utils.strings.transformers import build_remove_substrings

_strip_postgres_ft_operators = build_remove_substrings("&|!():*")

def fulltext_generator(query, column, *searches):
    return query.extra(where=[_ft_clause(column)], params=[_ft_terms(*searches)])

def _ft_terms(*searches):
    cleaned_searches = map(_strip_postgres_ft_operators, searches)
    return ' | '.join("(%s)" % ' & '.join(search.split()) for search in cleaned_searches)

def _ft_clause(column):
    return """to_tsvector('datacommons', %s) @@ to_tsquery('datacommons', %%s)""" % column