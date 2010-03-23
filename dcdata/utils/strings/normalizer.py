
"""
A collection of pre-configured normalizers.

Only one demo normalizer for now.
"""

from strings.transformers import compose, build_map_substrings, build_remove_substrings, build_remove_suffixes


basic_normalizer = compose(unicode.lower, 
                           build_map_substrings({' and ': '&'}),
                           build_remove_substrings(" ,.\"\'@+#$(){}[]\\&-/"),
                           build_remove_suffixes(['association', 'assoc', 'assn',
                                                 'incorporated', 'inc',
                                                 'company', 'co',
                                                 'corporation', 'corp',
                                                 'committee', 'cmte',
                                                 'limited', 'ltd']))