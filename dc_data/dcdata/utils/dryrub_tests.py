
import unittest
from hashlib import md5
from dryrub import MD5Filter

class TestMD5Filter(unittest.TestCase):
    def test_simple(self):
        f = MD5Filter((lambda r: r.get('contributor_urn', '')), 'contributor_entity')
        
        r = {'contributor_urn': '1234'}
        f.process_record(r)
        self.assertEqual(md5('1234').hexdigest(), r['contributor_entity'])

        r = {'some_other_field': '1234'}
        f.process_record(r)
        self.assertFalse(r.get('contributor_entity', False))
        
    def test_complicated(self):
        def generator(record):
            if record.get('organization_ext_id', False):
                return record['organization_ext_id']
            if record.get('organization_name', False):
                return 'urn:matchbox:organization:' + record['organization_name']
        
        f = MD5Filter(generator, 'organization_entity')
        
        r = {'some_other_field': '1234'}
        f.process_record(r)
        self.assertFalse(r.get('organization_entity', False))

        r = {'organization_ext_id': '1234'}
        f.process_record(r)
        self.assertEqual(md5('1234').hexdigest(), r['organization_entity'])
        
        r = {'organization_name': '1234'}
        f.process_record(r)
        self.assertEqual(md5('urn:matchbox:organization:1234').hexdigest(), r['organization_entity'])