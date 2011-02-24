import os
import re
import csv
import json
from collections import defaultdict

from django.conf import settings

from dcentity.tools import utils

# dict mapping all brisket last names to lists of politician entities.
ALL_POLITICIANS = defaultdict(list)

# List of nicknames, used for fuzzy name matching.
NICKNAMES_FILE = utils.path_relative_to(__file__, "nicknames.txt")
NICKNAMES = defaultdict(set)

ABBREVIATIONS = {
    'assn': 'association',
    'cmte': 'committee',
    'cltn': 'coalition',
    'inst': 'institute',
    'co': 'company',
    'corp': 'corporation',
    'us': 'united states',
    'dept': 'department',
    'assoc': 'associates',
    'natl': 'national',
}

def fix_name(name):
    name = re.sub("\s+\([\w ]+\)", "", name)
    if name.find(",") != -1 and not re.search("(et al| inc)", name, re.I):
        match = re.match("^(.*?)( (?:JR|SR|I+))?$", name.strip())
        if match:
            name, suffix = match.groups()
        else:
            suffix = None
        # Split by special chars (e.g. &'s, etc) which join
        # multiple names or names and non-name words.
        parts = re.split("(\s?[^A-Za-z0-9\s,']\s?)", name)
        # Reverse words before and after commas.
        decommaed = [" ".join(reversed(p.split(", "))) for p in parts]
        if suffix:
            decommaed.append(suffix)
        name = "".join(decommaed)
        # remove Mr and Mrs
        name = re.compile("^(DR|MR|MRS|MS) ", re.I).sub('', name)
    name = name.strip()
    # expand abbreviations
    name = " ".join(ABBREVIATIONS.get(w.lower(), w) for w in name.split())
    return name


class PersonName(object):
    """
    Object representing a person's name in western first, middle, last form.
    Allows matching different formulations of a name which include first,
    middle, last or suffixes. 
    """
    def __init__(self, name):
        self.name = name

        # Ignore ampersand and following
        name = name.split(' & ')[0]

        # Split out inline nicknames
        nick = None
        if '"' in name:
            try:
                start, nick, end = re.match("^(.*?) \"(.*?)\" (.*?)$", name).groups()
                name = " ".join((start, end))
            except AttributeError:
                pass

        # Remove suffix
        parts = [self.clean(p) for p in name.split()]
        if re.search("(^I+$|JR|SR)", parts[-1]):
            self.suffix = parts.pop(-1)
        else:
            self.suffix = None

        # Set first, middle, and last names
        self.first, self.middle, self.last = (None, None, None)
        if len(parts) == 1:
            self.last = parts[0]
        if len(parts) > 1:
            self.first = parts[0]
            self.last = parts[-1]
        if len(parts) > 2:
            self.middle = " ".join(parts[1:-1])

        # Process extra nicknames
        self.extra_nicks = {}
        if nick:
            nameset = set((self.first, self.clean(nick)))
            for name in nameset:
                self.extra_nicks[name] = nameset
    
    def matches(self, pname, **kwargs):
        """
        Accepts several kwargs to determine just how fuzzy to match.  No kwargs
        means maximum fuzziness.        

        exact (default False): shortcut to require exact name matches.
            Setting this changes all other switches to default to 'False',
            which can be overridden by explicitly setting them True.

        nicknames (default True): allow nicknames to match; 
            e.g. "Ted" matches "Theodore".  
        first_as_middle (default True): allow first names to match against
            middle names when a first or middle is missing.  
            e.g. "J. Edgar Hoover" matches "Edgar Hoover"
        missing_first (default True): allow first names to be skipped.
            e.g. "George Washington" matches "Washington"
        missing_middle (default True): allow middle names to be skipped.
            e.g. "Barack Hussein Obama" matches "Barack Obama"
        initials (default True): allow initials to stand in for full names.
            e.g. "B H Obama" matches "Barack Hussein Obama"
        missing_suffix (default True): Allow suffixes to go missing.  
            e.g. "Barack Obama Sr" matches "Barack Obama"
        """
        if isinstance(pname, basestring):
            return self.matches(PersonName(pname), **kwargs)

        elif isinstance(pname, OrganizationName):
            return self.matches(pname.pname, **kwargs)

        elif not isinstance(pname, PersonName):
            return False

        exact = kwargs.get('exact', False)
        default = not exact
        missing_suffix = kwargs.get('missing_suffix', default)
        nicknames = kwargs.get('nicknames', default)
        first_as_middle = kwargs.get('first_as_middle', default)
        initials = kwargs.get('initials', default)
        missing_middle = kwargs.get('missing_middle', default)
        missing_first = kwargs.get('missing_first', default)

        # Early out for names we can't parse correctly, or which fully match
        # anyway.
        if self.clean(self.name) == self.clean(pname.name):
            return True

        # Last names must match.
        if self.last and self.last != pname.last:
            return False

        # Suffixes must match, if present in both.
        if self.suffix != pname.suffix and (
                (self.suffix and pname.suffix) or not missing_suffix):
            return False

        # Missing first and middle names both (last and suffixes only)
        if missing_first and (
                (not self.first and not self.middle) or
                (not pname.first and not pname.middle)):
            return True

        if nicknames:
            nick_dicts = (get_nicknames(), self.extra_nicks, pname.extra_nicks)
        else:
            nick_dicts = ()

        # First name and middle name matched by "first as middle"
        if first_as_middle and self.match_middle_as_first(self, pname, 
                initials, *nick_dicts):
            return True

        # First names 
        if not self.match_as_first_names(self.first, pname.first, 
                initials, *nick_dicts):
            return False

        # And finally, middle names
        return (
            (self.middle == pname.middle) or
            (missing_middle and (not self.middle or not pname.middle)) or
            (initials and (self.name_or_initial(self.middle, pname.middle)))
        )

    def __eq__(self, pname):
        return self.matches(pname)

    def __ne__(self, pname):
        return not (self == pname)

    def __repr__(self):
        return '<PersonName("%s")>' % self.name

    def search_string(self):
        """ Include only first and last name in search string, unless we
        couldn't parse the name. """
        if self.first and self.last:
            return " ".join((self.first, self.last))
        else:
            return self.name

    @classmethod
    def match_middle_as_first(cls, pname1, pname2, initials, *nick_dicts):
        # once for each order
        for p1, p2 in ((pname1, pname2), (pname2, pname1)):
            if p1.first and p1.middle and not p2.middle and \
                    cls.match_as_first_names(p1.middle, p2.first,
                            initials, *nick_dicts):
                return True
        return False

    @classmethod
    def match_as_first_names(cls, name1, name2, initials, *nick_dicts):
        return (cls.name_or_nickname(name1, name2, *nick_dicts) or
            (initials and cls.name_or_initial(name1, name2)))

    @classmethod
    def name_or_nickname(cls, name1, name2, *args):
        if name1 == name2:
            return True
        for nick_dict in args:
            if name1 in nick_dict and name2 in nick_dict[name1]:
                return True
        return False

    @classmethod
    def clean(cls, string):
        return re.sub(u"[^A-Z]", "", string.upper())

    @classmethod
    def name_or_initial(self, name1, name2):
        return name1 == name2 or bool(name1 and name2 and (
            (len(name1) == 1 and name1 == name2[0]) or \
            (len(name2) == 1 and name1[0] == name2)
        ))

class OrganizationName(object):

    normalize_incs = {
        'CO': 'COMPANY',
        'CORP': 'CORPORATION',
        'INC': 'INCORPORATED',
    }

    individual_pac_patterns = (
        r'^(?:friends|citizens|committee|people|neighbors)(?: united)? (?:of|for|to (?:re)?elect) (.*?)(?: \d+)?$',
        r"^(?:friends of )?(.*?)(?: for)(?: (assembly|congress|council|rep|representative|senate|mayor|house|campaign|committee|state|us|exploratory|['\d]+))+$",
        r"^(.*?)(?: (campaign|committee))+$",
    )

    inc_re = "^(.*?)(?:,?\s+" + \
                "(llc|inc|incorporated|plc|co|corp|corporation|company)" + \
             ")?\.?$"

    def __init__(self, name):
        self.name = name 
        base_name, inc = re.match(self.inc_re, name, re.I).groups()
        self.base_name = self.clean(base_name)
        self.inc = self.clean(inc)
        self._is_politician = False

        self.pname = None
        if not self.inc:
            for pattern in self.individual_pac_patterns:
                match = re.match(pattern, name, re.I)
                if match:
                    self.base_name = match.group(1)
                    self.pname = PersonName(self.base_name)
                    break

            if not self.pname:
                parts = self.base_name.split()
                if len(parts) == 3 and \
                        parts[0] in get_nicknames() and len(parts[1]) == 1:
                    self.pname = PersonName(self.base_name)

    @classmethod
    def clean(cls, string):
        if string is None:
            return string
        # remove special chars
        string = re.sub("[^-A-Z0-9 ]", "", string.upper())
        # remove 'of' and 'the'
        # remove duplicate whitespace
        string = re.sub("\s+", " ", string.strip())
        return cls.normalize_incs.get(string, string)

    @classmethod
    def eq_clean(cls, string):
        # extra cleaning before equality checks
        string = re.sub("[^A-Z0-9 ]", "", string.upper())
        string = re.sub("( |^)(OF|THE)(?=$|\s)", "", string)
        return string.strip()

    def __eq__(self, other):
        if isinstance(other, basestring):
            return self == OrganizationName(other)

        elif isinstance(other, OrganizationName):
            if self.inc and other.inc and self.inc != other.inc:
                return False

            if self.pname and other.pname:
                return self.pname == other.pname

            return self.eq_clean(self.base_name) == \
                   self.eq_clean(other.base_name)

        elif isinstance(other, PersonName):
            return self.pname == other

        return False

    def __ne__(self, other):
        return not (self == other)

    def __repr__(self):
        return '<OrganizationName("%s")>' % self.name

    def search_string(self):
        if self.pname:
            return self.pname.search_string()
        elif self.base_name:
            return self.base_name
        return self.name

    def is_company(self):
        return bool(self.inc)

    def is_politician(self):
        return bool(self.pname)

    def is_pac(self):
        return bool(self.pname) or bool(re.search(" for ", self.name, re.I))

def get_nicknames():
    if len(NICKNAMES) == 0:
        with open(NICKNAMES_FILE) as fh:
            for row in fh:
                name_set = set(n.upper().strip() for n in row.split(","))
                for name in name_set:
                    NICKNAMES[name] |= name_set
    return NICKNAMES
