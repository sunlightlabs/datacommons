from django.template.loader import render_to_string
from locksmith.auth.models import ApiKey
from piston.handler import BaseHandler
from piston.utils import rc
from urllib import urlencode
import os

RAPPORTIVE_APIKEY = '34c1b7c631c94d57a241a107fb0b0bce'
STATIC_DIR = os.path.dirname(os.path.abspath(__file__)) + "/static"

def get_file_contents(filename):
	file = open(filename)
	out = file.read()
	file.close
	return out

class RapletHandler(BaseHandler):
    
    def read(self, request):
        # get system API key that client will use
        request.apikey = ApiKey.objects.get(key=RAPPORTIVE_APIKEY, status='A')
        
        # create response
        host = {'host' : 'http://%s' % request.META['HTTP_HOST']}
        response = {
            'html': render_to_string('pg_rapportive/poligraft.html'),
            'js': render_to_string('pg_rapportive/poligraft.js', host),
            'css': render_to_string('pg_rapportive/poligraft.css', host),
        }
        
        # return previously created response
        
        return response
