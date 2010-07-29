import re
import os
import time
import datetime
import traceback

from django.core.management.base import BaseCommand
from django.conf import settings

from dcentity.tools.models import EntityPlus
from dcentity.tools import wpapi
from dcentity.tools.names import PersonName, OrganizationName
from dcentity.tools import utils

def find_wikipedia_url(entity):
    """
    Returns a tuple of (url, article excerpt) for a given entity, or None if no
    matching article is found.

    >>> e = EntityPlus.objects.create(type='politician', name="foo")
    >>> a = e.aliases.create(alias='Barack Obama')
    >>> find_wikipedia_url(e)[0]
    'http://en.wikipedia.org/wiki/Barack_Obama'

    >>> e = EntityPlus.objects.create(type='organization', name="foo1")
    >>> a = e.aliases.create(alias='Atlantic Richfield')
    >>> find_wikipedia_url(e)[0]
    'http://en.wikipedia.org/wiki/ARCO'

    >>> e = EntityPlus.objects.create(type='organization', name="foo2")
    >>> a = e.aliases.create(alias='No WP entry for this')
    >>> print find_wikipedia_url(e)
    None

    >>> e = EntityPlus.objects.create(type='organization', name="foo4")
    >>> a = e.aliases.create(alias='159 Group')
    >>> print find_wikipedia_url(e)
    None

    >>> e = EntityPlus.objects.create(type='organization', name="foo5")
    >>> a = e.aliases.create(alias='188 Claremont')
    >>> print find_wikipedia_url(e)
    None

    """
    if entity.type == 'individual':
        return None

    for ename in entity.names:
        # Search for exact title matches with redirects.  Use for comparing
        # titles later -- we might exactly match a redirect title, but not
        # match the destination page at all.  Full text search returns only
        # the destination pages, not the redirections.
        redirects = wpapi.title_search_redirects(ename.search_string()) 

        # Full text search!
        results = wpapi.full_text_search(entity.get_search_terms(ename))
        for result in results:
            article = wpapi.WikipediaArticle(result['title'])
            # Exclude special namespaced articles (e.g. User:, Template:,
            # etc.)
            if (article.namespace or article.title.startswith("List of") or
                    article.is_disambiguation_page()):
                continue

            if article.title in redirects:
                name_comp = wpapi.WikipediaArticle(redirects.get(article.title)).name
            else:
                name_comp = article.name

            if entity.type == 'politician':
                if ename != PersonName(name_comp):
                    continue
                if not article.is_politician():
                    continue
                if not article.is_american():
                    continue
                subject = article.get_subject()
                if subject and ename != PersonName(article.get_subject()):
                    continue

            elif entity.type == 'organization':
                if ename.is_politician():
                    if ename.pname != PersonName(name_comp):
                        continue
                    if not article.is_politician():
                        continue
                    if not article.is_american():
                        continue
                else:
                    if ename != OrganizationName(name_comp):
                        continue
                    if article.is_person():
                        continue
                    if ename.is_company() and not article.is_company():
                        continue
            wikipedia_url = wpapi.article_url(article.title)
            wikipedia_excerpt = wpapi.get_article_excerpt(article.title)
            return (wikipedia_url, wikipedia_excerpt)
    return None

class Command(BaseCommand):
    args = '<output_file>'
    help = """Fetch wikipedia matches for all entities.  Requires one argument,
<output_file>, which is a CSV file to which results will be written.  The
results will include:

    entity_id, wikipedia_url or '', wikipedia_excerpt or '', datetime of fetch
    
Entries are not overridden -- if the file already contains a match for a given
entity_id, it will not be re-queried.  It should thus be efficient to restart
the process.  If you wish to refresh an entity, delete the row or start with a
fresh file.
"""

    def handle(self, *args, **kwargs):
        if len(args) < 1:
            print "Requires one argument: <output_file>"
            print
            print self.help
            return
        output_file = args[0]

        # Set up error logger
        error_file_name = "%s.errors%s" % os.path.splitext(output_file)
        while os.path.exists(error_file_name):
            error_file_name += "_"
        errors = open(error_file_name, 'w')
        error_writer = utils.UnicodeWriter(errors)

        # Retrieve previous results
        results = {}
        if os.path.exists(output_file):
            with open(output_file) as fh:
                reader = utils.UnicodeReader(fh)
                for row in reader:
                    results[row[0]] = row

        # Fetch and record new results
        with open(output_file, 'w') as fh:
            writer = utils.UnicodeWriter(fh)
            for eid, row in results.iteritems():
                writer.writerow(row)

            start = time.time()
            qs = EntityPlus.objects.exclude(type='individual')
            total = qs.count()
            count = 0
            for c, entity in enumerate(qs):
                if entity.id in results:
                    continue
                # counts the ones we're  not skipping
                count += 1

                try:
                    result = find_wikipedia_url(entity) or ['', '']
                    raise Exception("Hey there!")
                except Exception as e:
                    print "EXCEPTION", traceback.format_exc()
                    error_writer.writerow((entity.id, entity.names[0].name,
                        str(e.args), traceback.format_exc()))
                else:
                    row = (entity.id, 
                           result[0],
                           result[1],
                           unicode(datetime.datetime.now()))
                    results[row[0]] = row
                    writer.writerow(row)
                    print "%i/%i" % (c, total), \
                        (entity.names[0].name, result[0]), \
                        "average:", "%.02f" % ((time.time()-start)/count), \
                        "seconds"
