
import json
import urllib
import urllib2
import sys
import csv


def geocode_msa(name):
    endpoint = 'http://maps.googleapis.com/maps/api/geocode/json'
    
    url = urllib2.urlopen(endpoint + '?' + urllib.urlencode(dict(address=name, sensor='false')))
    
    result = json.loads(url.read())
    
    if result['status'] != 'OK':
        raise Exception("geocoding returned status %s" % result.get('status', None))

    if len(result['results']) != 1:
        raise Exception("geocoding return %d results" % len(result['results']))
    
    loc = result['results'][0]['geometry']['location']
    
    return (loc['lat'], loc['lng'])



if __name__ == "__main__":
    in_file = csv.DictReader(open(sys.argv[1], 'r'))
    out_file = csv.writer(open(sys.argv[2], 'w'))
    
    out_file.writerow(['msa_name', 'query', 'lat', 'lng', 'error'])
    
    tries = 0
    errors = 0
    
    for line in in_file:
        if line['lat'] and line['lng']:
            # rewrite row unmodified
            out_file.writerow([line[k] for k in ['msa_name', 'query', 'lat', 'lng', 'error']])
        else:
            try:
                tries += 1
                (lat, lng) = geocode_msa(line['query'])
                out_file.writerow([line['msa_name'], line['query'], lat, lng, ''])
                
            except Exception as e:
                out_file.writerow([line['msa_name'], line['query'], '', '', e])
                errors += 1
            
    print "Geocoded %d out of %d MSAs" % (tries - errors, tries)


