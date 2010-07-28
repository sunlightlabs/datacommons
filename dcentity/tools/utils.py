import re
import os
import csv
from collections import defaultdict

from django.contrib.localflavor.us.us_states import STATE_CHOICES

# Dict mapping state abbreviations to full state names
EXPAND_STATES = dict(STATE_CHOICES)
# Regular expression to match against any of the 50 states and 'america'
AMERICA_STATE_RE = re.compile(
        "(%s)" % ("america|" + "|".join(v for k,v in STATE_CHOICES)), 
        re.I)
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

def expand_state(state):
    return EXPAND_STATES.get(state, state)

def fix_name(name):
    """
    >>> fix_name('Joe Blow (D)')
    'Joe Blow'
    >>> fix_name('Blow, Joe (R)')
    'Joe Blow'
    >>> fix_name('Schumer, Ted & George, Boy')
    'Ted Schumer & Boy George'
    >>> fix_name('54th Natl Assn of US Cmte Dept Assoc Inc.')
    '54th national association of united states committee department associates Inc.'
    >>> fix_name('Johnson, Smith et al')
    'Johnson, Smith et al'
    >>> fix_name('GORDNER, FRIENDS OF JOHN')
    'FRIENDS OF JOHN GORDNER'
    >>> fix_name('HUFFMAN FOR ASSEMBLY 2008, JARED')
    'JARED HUFFMAN FOR ASSEMBLY 2008'
    >>> fix_name('BEHNING, CMTE TO ELECT ROBERT W')
    'committee TO ELECT ROBERT W BEHNING'
    >>> fix_name('HALL, DUANE R II')
    'DUANE R HALL II'
    >>> fix_name('WALL, TROSSIE W JR')
    'TROSSIE W WALL JR'
    >>> fix_name('CROOK, MRS JERRY W')
    'JERRY W CROOK'
    >>> fix_name('HAMRIC, PEGGY (COMMITTEE 1)')
    'PEGGY HAMRIC'
    """
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

def fix_dict_keys(unicode_dict):
    return dict((str(k), v) for k,v in unicode_dict.iteritems())

# The following taken from python standard library docs for unicode CSV writing
# and reading:

import csv, codecs, cStringIO

class UTF8Recoder:
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-8
    """
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode("utf-8")

class UnicodeReader:
    """
    A CSV reader which will iterate over lines in the CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        f = UTF8Recoder(f, encoding)
        self.reader = csv.reader(f, dialect=dialect, **kwds)

    def next(self):
        row = self.reader.next()
        return [unicode(s, "utf-8") for s in row]

    def __iter__(self):
        return self

class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)
