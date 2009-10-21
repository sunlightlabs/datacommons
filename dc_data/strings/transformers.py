"""
A collection of functions that are useful for building string normalizers.
"""

import re


def compose(*transforms):
    """ 
    Return a function that is the composition of the given list of functions.
        
    For example, compose(a, b, c)(x) is equivalent to calling c(b(a(x))). 
    """
        
    def rec_compose(input, functions):
        if functions:
            first = functions[0]
            rest = functions[1:]
            return rec_compose(first(input),rest)
        else:
            return input
    return lambda x: rec_compose(x,transforms)


def build_remove_substrings(substrings):
    """ Return a function that will remove all occurrences of any string in the given list. """
    
    return _build_generic_remove("%s",substrings)


def build_remove_suffixes(suffixes):
    """ Return a function that will remove any suffix in the given list. """
    
    return _build_generic_remove("(%s)$",suffixes)


def build_remove_prefixes(prefixes):
    """ Return a function that will remove any prefix in the given list. """
    return _build_generic_remove("^(%s)", prefixes)


def build_map_substrings(mappings):
    """ Return a function that will map all occurrences of key strings to their associated value. """
    
    return _build_generic_mapper("(%s)",mappings.keys(), lambda match: mappings[match.group(0)])


def _build_generic_remove(pattern,strings):
    return _build_generic_mapper(pattern, strings, lambda match: "")    


def _build_generic_mapper(pattern,triggers,mapper):
    
    pattern = pattern % "|".join([re.escape(s) for s in triggers])
    exp = re.compile(pattern)
    return lambda input: re.sub(exp, mapper, input)



"""
To do--other transformers that might be useful:
    - a complete regex capture transform: take in a regex to run on the entire string, and an output based on capture groups
"""
    


