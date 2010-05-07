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

class RapletHandler(BaseHandler):
    
    def read(self, request):

        request.apikey = ApiKey.objects.get(key=settings.SYSTEM_API_KEY, status='A')
        
        name = request.GET.get('name', '').replace('+', ' ')
        callback = request.GET.get('callback', None)
        
        if not name or not callback:
            return rc.BAD_REQUEST('name and callback parameters are required')
        
        contributions = load_contributions({
            'contributor_ft': name,
            'cycle': str(CYCLE),
            'for_against': 'for',
            'per_page': 5,
        }, ordering='-amount')
        
        lobbying = load_lobbying({
            'lobbyist_ft': name,
            'year': str(CYCLE),
        })
        
        response = {
            'html': render_to_string('rapportive/raplet.html', {
                'lobbying': lobbying,
                'lobbying_hash': b64encode(
                    urlencode({
                        'lobbyist_ft': name,
                        'year': str(CYCLE),
                    }).replace('+', ' ')
                ),
                'contributions': contributions,
                'contributions_hash': b64encode(
                    urlencode({
                        'contributor_ft': name,
                        'cycle': str(CYCLE),
                        'for_against': 'for',
                    }).replace('+', ' ')
                ),
                'cycle': '%s-%s' % (CYCLE - 1, CYCLE),
                'name': name,
            }),
            'css': render_to_string('rapportive/raplet.css'),
        }
        
        return response