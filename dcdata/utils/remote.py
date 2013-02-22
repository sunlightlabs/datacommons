import urllib2
import urllib
import time
import os
import dateutil


class _HeadRequest(urllib2.Request):
    def get_method(self):
        return "HEAD"


def get_header(url):
    response = urllib2.urlopen(_HeadRequest(url))
    return response.info()


def fetch_if_updated(url, local_path):
    """Check if the file at remote URL is newer than file at local path. If so, overwrite.
    
    Returns true if file was updated, false otherwise.
    """
    
    local_date = time.localtime(os.path.getctime(local_path)) if os.path.exists(local_path) else None
    if local_date:
        remote_date = dateutil.parser.parse(get_header(url)['Date'])
        if remote_date < local_date:
            return False
        
    urllib.urlretrieve(url, local_path)
    
    
    