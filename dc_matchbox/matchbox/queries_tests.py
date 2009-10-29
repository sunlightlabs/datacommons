
import unittest
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'


from queries import _prepend_pluses



class Test(unittest.TestCase):

    def test_prepend_pluses(self):
        self.assertEqual("", _prepend_pluses(""))
        self.assertEqual("", _prepend_pluses("   "))
        
        self.assertEqual("+a", _prepend_pluses("a"))
        self.assertEqual("+apple +computer", _prepend_pluses("apple computer"))
        self.assertEqual("+apple +computer, +inc.", _prepend_pluses("apple computer, inc."))
        self.assertEqual("+Procter +& +Gamble", _prepend_pluses("Procter & Gamble"))
        self.assertEqual("+Emily's +List", _prepend_pluses("Emily's List"))
        