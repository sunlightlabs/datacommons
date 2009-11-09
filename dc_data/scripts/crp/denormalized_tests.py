
import unittest

from denormalize_indiv import OrganizationFilter

class Tests(unittest.TestCase):
    
    def test_organization_filter(self):
        f = OrganizationFilter()
        
        r = {'org_name': "normal enough company name"}
        f.process_record(r)
        self.assertEqual("normal enough company name", r['organization_name'])
        
        r = {'org_name': "Self Employed", 'emp_ef': "normal enough company name"}
        f.process_record(r)
        self.assertEqual("normal enough company name", r['organization_name'])

        r = {'emp_ef': "normal enough company name"}
        f.process_record(r)
        self.assertEqual("normal enough company name", r['organization_name'])
        
        r = {'org_name': 'Filmmaker', 'emp_ef': 'Writer', 'fec_occ_emp': "normal enough company name/CEO"}
        f.process_record(r)
        self.assertEqual("normal enough company name", r['organization_name'])       
        
        r = {}
        f.process_record(r)
        self.assertEqual(None, r['organization_name'])
        
        