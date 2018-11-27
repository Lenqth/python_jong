
import sys,os
sys.path.append( os.path.dirname( os.path.dirname(__file__) ) )

import unittest
from judge.agari import *

class TestAgari(unittest.TestCase):

    def test_kokushi(self):
        self.assertIsNotNone( agari_kokushi( string_to_array("19m19p19sNEWSHRG1m") ))
        self.assertIsNotNone( agari_kokushi( string_to_array("19m19p19sNEWSHRGG") ))

        self.assertIsNone( agari_kokushi( string_to_array("19m11p19sNEWSHRGG") ))
        self.assertIsNone( agari_kokushi( string_to_array("19m11p179sNEWSHRG") ))
        self.assertIsNone( agari_kokushi( string_to_array("19m1p19sNEWSHRGGG") ))

    def test_7pairs(self):
        self.assertIsNotNone( agari_7pairs( string_to_array("11335577m224466p") ))
        self.assertIsNotNone( agari_7pairs( string_to_array("11335577m2266pSS") ))
        self.assertIsNotNone( agari_7pairs( string_to_array("1111m225599pSSHH") ))
        self.assertIsNone( agari_7pairs( string_to_array("11335567m2266pSS") ))

        # # DISALLOW FOUR
        #ALLOW_FOUR_IN_7PAIRS = False
        #self.assertIsNone( agari_7pairs( string_to_array("11335567m2266pSS") ))

    def test_knitted(self):
        self.assertIsNotNone( agari_knitted( to_array(man="147",pin="28",sou="369",ji="1234567") ))

    def test_knitted_normal(self):
        self.assertIsNotNone( agari_knitted_normal( to_array(man="147",pin="25811",sou="369567") ))

    def test_normal(self):
        self.assertIsNotNone( agari_normal( to_array(man="123",pin="456",sou="789",ji="11122") ))
        self.assertIsNone( agari_normal( to_array(man="123",pin="456",sou="789",ji="12344") ))

    def test_total(self):
        self.assertIsNotNone( is_agari( to_array(man="147",pin="25811",sou="369567") ))
        self.assertIsNotNone( is_agari( to_array(man="147",pin="28",sou="369",ji="1234567") ))
        self.assertIsNone( is_agari( string_to_array("147m3469p1258sSSG") ))
        self.assertIsNotNone( is_agari( string_to_array("123234345m67888p") ))
        self.assertIsNotNone( is_agari( string_to_array("55678s45667p5p") , exposed_mentu = 1 ))


        
if __name__ == "__main__":
    from pprint import pprint
    unittest.main()
