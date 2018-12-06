import unittest
from games.jong.judge.util import *
from games.jong.judge.shanten import *

#import cProfile
#cProfile.run("""
#from games.jong.judge.util import *
#from games.jong.judge.shanten import *
#[ shanten(randomhand()) for i in range(1000) ]
#""")
class TestShanten(unittest.TestCase):

    def test_kokushi(self):
        self.assertEqual( 0 , shanten_kokushi( to_array(man="19",pin="19",sou="199",ji="123456") ) )

    def test_7pairs(self):
        self.assertEqual( 1 , shanten_7pairs( to_array(man="11",pin="225566",sou="34",ji="133") ) )

    def test_knitted(self):
        self.assertEqual( 0 , shanten_knitted( to_array(man="147",pin="25",sou="3",ji="12345567") ) )

    def test_knitted_normal(self):
        self.assertEqual( 0 , shanten_knitted_normal( to_array(man="147",pin="258",sou="369167",ji="33") ) )
        self.assertEqual( 2 , shanten_knitted_normal( to_array(man="1236",pin="2347",sou="258",ji="155") ) )
        #12344567 - 258 - 36 - 白 : 一向聴
        self.assertEqual( 1 , shanten_knitted_normal( to_array(man="12344567",pin="258",sou="36",ji="5") ) )

    def test_normal(self):
        self.assertEqual( 1 , shanten_normal( to_array(man="11123678999",pin="19",sou="",ji="") ) )

    def test_total(self):
        #12344567 - 258 - 36 - 白 : 一向聴
        self.assertEqual( 1 , shanten( to_array(man="12344567",pin="258",sou="36",ji="5") ) )
        #3456 - 2345 - 147 - 白発中 : 三向聴
        self.assertEqual( 3 , shanten( to_array(man="3456",pin="2345",sou="147",ji="567") ) )
        # 1236 - 2347 - 258 - 東白白 : 二向聴
        self.assertEqual( 2 , shanten( to_array(man="1236",pin="2347",sou="258",ji="155") ) )