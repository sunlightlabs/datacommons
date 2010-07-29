import re
import sys
import json
import gzip
import urllib
import urllib2
import lxml.etree
try:
    import hashlib
    md5 = hashlib.md5
except ImportError:
    # for Python << 2.5
    import md5 as md5_lib
    md5 = md5_lib.new()
import cStringIO as StringIO

from django.conf import settings
from django.core.cache import cache
from django.utils.encoding import smart_str
from django.contrib.localflavor.us.us_states import STATE_CHOICES

from dcentity.tools import names

WIKIPEDIA_API_URL = "http://en.wikipedia.org/w/api.php"
WIKIPEDIA_PARSER = lxml.etree.XMLParser(
        dtd_validation=False,
        load_dtd=False,
        resolve_entities=False,
        encoding="utf-8",
        recover=True,
)

# Regular expression to match against any of the 50 states and 'america'
AMERICA_STATE_RE = re.compile(
        "(%s)" % ("america|" + "|".join(v for k,v in STATE_CHOICES)), 
        re.I)

def build_cache_key(*parts):
    key = u"/".join((settings.CACHE_PREFIX,) + parts)
    return md5(key.encode('utf-8')).hexdigest()

def wikipedia_api_query(params):
    # ensure k/v are sorted so we don't miss cache due to different ordering
    key = build_cache_key(
        u"wikipedia-api", 
        u"&".join(u"%s=%s" % (k, v) for k,v in sorted(params.items()))
    )
    cached = cache.get(key)
    try:
        if cached:
            return json.loads(cached)
    except ValueError:
        pass

    for k in params:
        params[k] = params[k].encode('utf-8')
    url = "%s?%s" % (WIKIPEDIA_API_URL, urllib.urlencode(params))
    #print >> sys.stderr, url
    fh = urllib.urlopen(url)
    text = fh.read()
    cache.set(key, text)
    return json.loads(text)

def title_search_redirects(phrase):
    """
    Construct a dict mapping destination => redirecting page given a phrase
    that might be a redirecting page title.  

    >>> title_search_redirects(u"Atlantic Richfield")
    {u'ARCO': u'Atlantic Richfield'}

    >>> title_search_redirects(u"PANERA")
    {u'Panera Bread': u'PANERA'}

    >>> title_search_redirects(u"Barack Obama")
    {u'Barack Obama': u'Barack Obama'}

    """
    redirects = {}
    # Get redirects for any title matches.
    clean_name = clean(phrase)
    for title in title_search(phrase):
        if clean_name == clean(title):
            redirect = get_redirect(title)
            if redirect:
                redirects[redirect] = phrase 

    # Also get redirects for the search phrase itself, which may not be
    # returned by the title search..
    redirect = get_redirect(phrase)
    if redirect and clean(redirect) != clean(phrase):
        redirects[redirect] = phrase
    return redirects

def clean(string):
    """
    >>> clean(u"PANERA >(@*#&")
    u'PANERA'
    """
    return re.sub("\s+", " ", re.sub("[^A-Z ]", " ", string.upper())).strip()

def get_redirect(title):
    """ 
    Find the destination to which the given title redirects, or None if it does
    not redirect.

    >>> get_redirect("Atlantic Richfield")
    u'ARCO'

    >>> get_redirect("PUEBLO OF LAGUNA")
    u'Laguna Pueblo'

    """
    title = wp_normalize(title)
    params = {
            'action': 'query',
            'titles': title,
            'redirects': "1",
            'format': 'json',
    }
    results = wikipedia_api_query(params)
    if results['query'].has_key('pages'):
        return results['query']['pages'].values()[0]['title']
    return None

non_caps = set("a an and as at but by en for if in of on or the to v v. via vs vs.".split())
def wp_normalize(string):
    """Wikipedia's redirect search is unfortunately very case-picky.  Try to
    normalize cases the way wikipedia does, so we can get proper matches.

    >>> wp_normalize("PUEBLO OF LAGUNA")
    'Pueblo of Laguna'

    >>> wp_normalize("the way of the tiger")
    'The Way of the Tiger'

    >>> wp_normalize("thl partners")
    'THL Partners'

    """
    # Wikipedia wants the first character of a title and any proper nouns in
    # the title capitalized.  Given our use case, assume everything is a proper
    # noun except the non_caps words above.
    words = string.lower().split()
    for i in range(len(words)):
        if words[i] not in non_caps:
            if not re.search("[aeiou]", words[i]):
                words[i] = words[i].upper()
            else:
                words[i] = words[i][0].upper() + words[i][1:]
    # Always cap first letter.
    words[0] = words[0][0].upper() + words[0][1:]
    return " ".join(words)


def title_from_url(url):
    """
    >>> title_from_url("http://en.wikipedia.org/wiki/Barack_Obama")
    'Barack Obama'
    """
    if url:
        return urllib.unquote(url.split("/")[-1].replace('_', ' '))
    return None

def article_url(title):
    """
    >>> article_url("Barack Obama")
    'http://en.wikipedia.org/wiki/Barack_Obama'

    """
    return "http://en.wikipedia.org/wiki/%s" % (
            urllib.quote(title.encode("utf-8").replace(" ", "_"))
    )

def full_text_search(phrase):
    params = {
        'format': 'json',
        'action': 'query',
        'list': 'search',
        'srsearch': phrase,
    }
    results = wikipedia_api_query(params)
    return [{
        'title': r['title'],
        'content': r['snippet'],
    } for r in results['query']['search']]

def get_article_categories(title):
    params = {
        'format': 'json',
        'action': 'query',
        'prop': 'categories',
        'titles': title,
    }
    results = wikipedia_api_query(params)
    try:
        return [r['title'] for r in results['query']['pages'].values()[0]['categories']]
    except KeyError:
        return []


def title_search(phrase):
    params = {
        'action': 'opensearch',
        'search': phrase,
    }
    results = wikipedia_api_query(params)
    return results[1]

article_xml_cache = {}
def get_article_xml(title):
    # temporary xml cache for process
    if article_xml_cache.get(title, None) is not None:
        return article_xml_cache[title]

    # longer term html memcached cache
    url = article_url(title)
    key = build_cache_key(url)
    cached = cache.get(key)
    if cached:
        html = cached
    else:
        #print >> sys.stderr, url
        opener = urllib2.build_opener()
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        fh = opener.open(url)
        # Handle gzip-encoded html from wikimedia's cache servers
        if fh.info().get('content-encoding', None) == 'gzip':
            gzipped = fh.read()
            data = StringIO.StringIO(gzipped)
            gzipper = gzip.GzipFile(fileobj=data)
            html = gzipper.read()
        else:
            html = fh.read()
        cache.set(key, html)
    xml = lxml.etree.fromstring(html, parser=WIKIPEDIA_PARSER)
    article_xml_cache[title] = xml
    return xml

def get_article_excerpt(title, length=500):
    """
    Extract the first few paragraphs of the given article until the length
    exceeds the given length (default 500 characters), or the article ends,
    whichever comes first.
    #>>> get_article_excerpt("Jim Keet")
    """
    xml = get_article_xml(title)
    # Get paragraphs that are immediate descendents of <div id="bodyContent">.
    # This should exclude infobox or other details outside the main article
    # body.
    paragraphs = xml.xpath('//x:div[@id="bodyContent"]/x:p', 
            namespaces={'x': 'http://www.w3.org/1999/xhtml'})
    char_count = 0
    excerpt = []
    for p in paragraphs:
        text = "".join(p.xpath('string()'))
        # remove citations -- we aren't pulling references in
        text = re.sub("\[\d+\]", " ", text)
        if text:
            excerpt.append(text)
            char_count += len(text)
            if char_count > length:
                break

    return "".join(u"<p>%s</p>" % p for p in excerpt)

def get_article_subject(title):
    """
    Extract the portion of the article in the first bolded bit of the first
    paragraph, which conventionally is the subject of the article, often in
    more detail than the title.

    >>> get_article_subject("Barack Obama")
    u'Barack Hussein Obama II'

    """
    xml = get_article_xml(title)
    try:
        return unicode(xml.xpath('//x:p[1]/x:b[1]/text()',
                namespaces={'x': 'http://www.w3.org/1999/xhtml'})[0])
    except IndexError:
        return None

class WikipediaArticle(object):
    """
    Class representing a Wikipedia Article, encapsulating properties such as
    the name, disambiguation, categories.  Makes calls to the wikipedia API to
    obtain data.

    >>> a = WikipediaArticle("Barack Obama")
    >>> a.is_person()
    True
    >>> a.is_politician()
    True
    >>> a.name_matches("Barack Hussein Obama III")
    True
    >>> a.is_american()
    True

    >>> a = WikipediaArticle("BP")
    >>> a.is_person()
    False
    >>> a.is_politician()
    False
    >>> a.is_company()
    True
    
    >>> a = WikipediaArticle("User:SomeUser (disambiguation)")
    >>> a.namespace
    'User'
    >>> a.name
    'SomeUser'
    >>> a.disambiguator
    'disambiguation'

    >>> a = WikipediaArticle("Ralph E. Reed, Jr.")
    >>> a.is_person()
    True
    >>> a.is_politician()
    True
    >>> a.is_american()
    True

    >>> a = WikipediaArticle("Brian Clay")
    >>> a.is_politician()
    False

    >>> a = WikipediaArticle("Kevin Kolb")
    >>> a.is_person()
    True
    >>> a.is_politician()
    False

    >>> a = WikipediaArticle("Linda Upmeyer")
    >>> a.is_politician()
    True
    >>> a.is_american()
    True

    >>> a = WikipediaArticle("Donald Morrison (politician)")
    >>> a.is_person()
    True
    >>> a.is_politician()
    True
    >>> a.is_american()
    False

    >>> WikipediaArticle("Robert Mendelsohn").is_disambiguation_page()
    True

    """
    def __init__(self, title):
        self.title = title
        self.namespace, self.name, self.disambiguator = re.match(
                r'^(?:(.*?):)?(.*?)(?:\s+\((.*?)\))?$', title).groups()
        self.disambiguator = (self.disambiguator or "").lower()
        self.categories = None
        self.excerpt = None

    def get_categories(self):
        if self.categories is None:
            self.categories = "|".join(
                c for c in get_article_categories(self.title)
            ).lower()
        return self.categories

    def get_excerpt(self):
        if self.excerpt is None:
            self.excerpt = get_article_excerpt(self.title)
        return self.excerpt

    def get_subject(self):
        return get_article_subject(self.title)

    def is_company(self):
        if "companies" in self.get_categories():
            return True
        return False

    def is_person(self):
        cats = self.get_categories()
        return bool(re.search(
            "(category:living people|deaths|politicians|births)", cats, re.I
        ))

    def is_american(self):
        return bool(AMERICA_STATE_RE.search(self.get_categories()))

    def is_politician(self):
        return self.is_person() and (
            ("politician" in self.disambiguator) or
            (self._politician_words(self.get_categories())) or
            (self._politician_words(self.get_excerpt()))
        )

    def is_disambiguation_page(self):
        return "disambiguation" in self.title.lower() or \
               "disambiguation" in self.get_categories()

    def _politician_words(self, string):
        return bool(re.search(r"(politician|republican|democrat|judge|governor|president of the united states|house of representatives|senate)", string, re.I))

    def name_matches(self, name):
        if self.is_person():
            return names.PersonName(self.name) == names.PersonName(name)
        else:
            return self.name == name

    def __repr__(self):
        return '<WikipediaArticle("%s")>' % self.title


