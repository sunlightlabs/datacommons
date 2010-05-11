from base64 import b64encode
from dcapi.contributions.handlers import load_contributions
from dcapi.lobbying.handlers import load_lobbying
from django.conf import settings
from django.template.loader import render_to_string
from locksmith.auth.models import ApiKey
from piston.handler import BaseHandler
from piston.utils import rc
from urllib import urlencode
#from dcdata.contributions.models import Contribution
#from dcdata.lobbying.models import Lobbying

CYCLE = 2008
RAPPORTIVE_APIKEY = '34c1b7c631c94d57a241a107fb0b0bce'

def make_hash(params):
    return b64encode(urlencode(params).replace('+', ' '))

class RapletHandler(BaseHandler):
    
    def read(self, request):

        # get system API key that client will use
        request.apikey = ApiKey.objects.get(key=RAPPORTIVE_APIKEY, status='A')
        
        # get parameters from request
        name = request.GET.get('name', '').replace('+', ' ')
        callback = request.GET.get('callback', None)
        if not name or not callback:
            return rc.BAD_REQUEST('name and callback parameters are required')
        
        # get contributions and create link hash for each contributor
        contributors = load_contributions({
            'contributor_ft': name,
            'cycle': str(CYCLE),
            'for_against': 'for',
            'per_page': 10,
        }, ordering='contributor_name').values('contributor_name','contributor_state','organization_name').distinct()
        
        for contrib in contributors:
            contrib['hash'] = make_hash({
                'contributor_ft': contrib['contributor_name'],
                'organization_ft': contrib['organization_name'],
                'cycle': str(CYCLE),
                'for_against': 'for',
            })
        
        # load lobbying records
        lobbying = load_lobbying({
            'lobbyist_ft': name,
            'year': str(CYCLE),
        })
        
        # create hashes for linking to transparency data
        contributor_hash = make_hash({
            'contributor_ft': name,
            'cycle': str(CYCLE),
            'for_against': 'for',
        })
        lobbying_hash = make_hash({
            'lobbyist_ft': name,
            'year': str(CYCLE),
        })
        
        # create response
        response = {
            'html': render_to_string('rapportive/raplet.html', {
                'lobbying': lobbying,
                'lobbying_hash': lobbying_hash,
                'contributors': contributors,
                'contributor_hash': contributor_hash,
                'cycle': '%s-%s' % (CYCLE - 1, CYCLE),
                'name': name,
            }),
            'css': render_to_string('rapportive/raplet.css'),
        }
        
        # return previously created response
        
        return response