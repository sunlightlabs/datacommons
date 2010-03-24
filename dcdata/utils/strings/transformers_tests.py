
import unittest

from dcdata.utils.strings.transformers import *

class Test(unittest.TestCase):
        
    def testBuildRemoveSubstrings(self):
        input = "Bananas are a very great fruit."
        
        remover = build_remove_substrings([])
        self.assertEqual(input,remover(input))
        
        remover = build_remove_substrings([""])
        self.assertEqual(input,remover(input))
        
        remover = build_remove_substrings(["a"])
        self.assertEqual("Bnns re  very gret fruit.",remover(input))
        
        remover = build_remove_substrings(["aeiou"])
        self.assertEqual(input,remover(input))
        
        remover = build_remove_substrings(["a","e","i","o","u"])
        self.assertEqual("Bnns r  vry grt frt.",remover(input))
        
        remover = build_remove_substrings(["ana"])
        self.assertEqual("Bnas are a very great fruit.",remover(input))
        
        remover = build_remove_substrings(["Ban","ana"])
        self.assertEqual("s are a very great fruit.",remover(input))
        
    def testBuildRemoveSuffixes(self):
        input1 = "Myco co"
        input2 = "Myco LLC"
        
        remover = build_remove_suffixes(["co","LLC"])
        
        self.assertEqual("Myco ",remover(input1))
        self.assertEqual("Myco ",remover(input2))
        
    def testBuildRemovePrefixes(self):
        input = "The Coca-Cola Company"
        
        remover = build_remove_prefixes(["The ", "Coca"])
        
        self.assertEqual("Coca-Cola Company",remover(input))
        
        
    def testBuildMapSubstrings(self):
        
        mapper = build_map_substrings({"\"":"\'", "#":"Number ", "$":"Dollar", "and":"&", "Company":"co"})

        self.assertEqual("The \'Whole Hog\' co",mapper("The \"Whole Hog\" Company"))
        self.assertEqual("Number 1 Cheap Dollar",mapper("#1 Cheap $"))
        self.assertEqual("Smith & Jones",mapper("Smith and Jones"))
        

    def test_compose(self):
        
        f = compose()
        self.assertEqual("arbitrary string",f("arbitrary string"))
        self.assertEqual(1234,f(1234))
        
        f = compose(lambda x: x + x)
        self.assertEqual(2468,f(1234))
        self.assertEqual("stringstring",f("string"))
        
        f = compose(lambda x: x * x, lambda x: x + x, lambda x: x + 1)
        self.assertEqual(51, f(5))
        
        f = compose(lambda x: x + 1, lambda x: x + x, lambda x: x * x)
        self.assertEqual(144, f(5))
        
        f = compose(str.lower, build_remove_substrings([' ','.', ',']))
        self.assertEqual('normalco',f('Nor, Mal. Co'))


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()