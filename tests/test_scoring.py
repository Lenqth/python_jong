# -*- coding : utf-8 -*- 

import sys,os

import unittest
from games.jong.judge.agari import *
from games.jong.judge.util import *
from games.jong.judge.scoring import ChineseScore

def tyaku(str) : 
    handtiles,exposed,tsumo = string_to_list_ex(str)
    env = {
        "prevalent_wind": -1 ,
        "seat_wind": -1,
        "tsumo":tsumo ,
        "deck_left":11,
        "discarded_tiles": [],
        "exposed_tiles": []
    }
    return ChineseScore.judge( handtiles,exposed,env )


class TestScore(unittest.TestCase):

    def assertYaku( self , s,q ):
        sc,y,sc2 = tyaku(s)
        yn = sorted( [ x.chinese_name for x in y ] )
        q = sorted(q)
        if yn == q :
            pass
        else:
            raise AssertionError(" Hand : %s , Expect : %s , Got : %s " % (s,q,yn))

    def test_7pairs(self):
        pass
        
    def test_knitted(self):
        self.assertYaku( "7m 258p 369s ESWNGR 1m!" , ["全不靠","不求人"] )
        self.assertYaku( "147m 28p 369s SWNGR 5p" , ["全不靠","組合龍"] )
        self.assertYaku( "7m 258p 369s ESWNGR H" , ["七星不靠"] )
        self.assertYaku( "147m 258p 369s 456m 7s 7s" , ["組合龍","平和","門前清","単調将"] )
        self.assertYaku( "147m 258p 369s 4567m 7m" , ["組合龍","平和","門前清"] )
        self.assertYaku( "147p 258s 369m RRR N N!" , ["組合龍","五門斉","箭刻","不求人","単調将"] )
    
    def test_concealed(self):
        self.assertYaku( "222m 444p 333s WWW 1p 1p" , ["三色三節高","么九刻","四暗刻","単調将"] )
        self.assertYaku( "222m 444p 333s 11p WW 1p" , ["三色三節高","么九刻","三暗刻","碰碰和","門前清"] )
        self.assertYaku( "111m *NNN 444p 99p 77m 7m!" , ["三暗刻","缺一門","自摸","么九刻","么九刻","碰碰和"] )
        self.assertYaku( "111m *NNN 444p 99p 77m 7m" , ["双暗刻","缺一門","么九刻","么九刻","碰碰和"] )
        self.assertYaku( "111m *NNN *444p 99p 77m 7m" , ["缺一門","么九刻","么九刻","碰碰和"] )
        self.assertYaku( "123m *234m *345m 77p GG 7p!" , ["一色三歩高", "缺一門","自摸"] )
    
    def test_chicken(self):
        self.assertYaku( "123m *777s *567p 56s WW 4s" , ["無番和"] )

    def test_ninegates(self):
        self.assertYaku( "1112345678999m 9m!" , ["九連宝燈","不求人","清龍","四帰一"] )
        self.assertYaku( "1112345678999m 6m!" , ["九連宝燈","不求人","連六"] )
        self.assertYaku( "1112345567999m 8m" , ['門前清', '么九刻', '么九刻', '双暗刻', '清一色'] ) # 中国麻雀では純正のみ
        self.assertYaku( "*345m 1112678999m 3m" , ["清一色","么九刻","連六"] ) # 鳴いてたら無効
    
    def test_tsumo(self):
        self.assertYaku( "2p *345s *456m *HHH *WWW 2p " , ["全求人","箭刻","么九刻","五門斉"] ) 
        self.assertYaku( "2p *345s *456m *HHH *WWW 2p! " , ["自摸","箭刻","么九刻","五門斉","単調将"] ) 
        self.assertYaku( "22p *345s *456m *HHH WW 2p " , ["箭刻","五門斉"] )  

    def test_chow_same(self):
        self.assertYaku( "*123p *123m *123s 234s4p 4p!" , ["三色三同順","小于五","自摸","単調将","平和"] ) 
        self.assertYaku( "*123p *123p 1223344p 4p!" , ["一色三同順","小于五","清一色","四帰一","四帰一","自摸","平和"] ) 
        self.assertYaku( "*123p *123p *123s *123m W W" , ["三色三同順","一般高","全求人","全帯么"] ) 


    def test_misc(self):
        self.assertYaku( "*888s *234s 66m 345p 67s 5s"  ,[ "連六","断么"] )
        self.assertYaku( "*678m *123s 44678s SS 4s!"  ,[ "自摸","喜相逢","缺一門" ] )
        self.assertYaku( "6m 147s 28p ESWNRGH 9m!"  ,[ "不求人" , "七星不靠" ] )
        self.assertYaku( "*567m 55678s 45667p 5p"  ,[ "三色三歩高", "平和","断么","喜相逢" ] )
        self.assertYaku( "*222p *333p 11199m 13s 2s"  ,[ "無字" , "么九刻" , "坎張" ] )
        self.assertYaku( "*123s *RRR 78s 123p WW 9s"  ,[ "全帯么" , "箭刻" , "缺一門" , "喜相逢" , "老少副" ] )
        self.assertYaku( "*123m *123s *444p 11m 22s 1m"  ,[ "喜相逢" , "么九刻" , "四帰一" , "小于五" ] )
        self.assertYaku( "*678p *EEE *WWWWk 4456p 4p"  ,[ "么九刻", "么九刻" , "明槓" , "混一色" ] )
        self.assertYaku( "*RRR 23s 123789p HH 4s"  ,[ '箭刻', '缺一門', '老少副' ] )
        self.assertYaku( "*567s 234s 2355789p 1p"  ,[ '平和', '缺一門', '老少副', '連六' ] )
        self.assertYaku( "*789m *123s 78899s RR 7s"  ,[ '一般高', '全帯么', '喜相逢', '缺一門', '老少副', '辺張' ] )
        self.assertYaku( "*456m *234p *456s 2288m 8m!"  ,[ '喜相逢', '断么', '自摸' ] )
        self.assertYaku( "*NNN *999m 67m 44s 678p 8m"  ,[ '么九刻', '么九刻', '喜相逢' ] )
        self.assertYaku( "*678p 234s 1134445p 1p!"  ,[ '么九刻', '無字', '缺一門', '自摸', '連六' ] )
        self.assertYaku( "*456p *789m *567s 5678p 5p"  ,[ '三色三歩高', '平和' ] )
        self.assertYaku( "*HHH *123m *RRRRk 78m EE 6m!"  ,[ '双箭刻', '明槓', '混一色', '自摸' ] )
        self.assertYaku( "67m 123456789s 99p 5m!"  ,[ '不求人', '平和', '清龍' ] )
        self.assertYaku( "12345679m 567s 77p 8m!"  ,[ '不求人', '坎張', '平和', '清龍' ] )
        self.assertYaku( "*HHH *345p 57m 11456s 6m!"  ,[ '三色三歩高', '坎張', '箭刻', '自摸' ] )
        self.assertYaku( "*SSS *777s *111m 888s H H!"  ,[ '么九刻', '么九刻', '単調将', '碰碰和', '缺一門', '自摸' ] )
        self.assertYaku( "*456p 1123478889p 1p!"  ,[ '么九刻', '清一色', '自摸', '連六' ] )
        self.assertYaku( "123456m 34566s 45p 6p!"  ,[ '不求人', '喜相逢', '平和', '連六' ] )

    def test_misc014(self):
        self.assertYaku( "22255m 345p 34s *GGG 2s!"  ,[ '箭刻', '自摸' ] ) # ? 
        self.assertYaku( "*123s *567s 88s 55789p 5p"  ,[ '無字', '缺一門' ] ) # ?
        self.assertYaku( "7m 258p 369s ESWNGR 1m!"  ,[ '不求人', '全不靠' ] ) # ?
                

        #print( testyaku( "*5555pk *111p *999s 3377m 3m"  ) )
        #print( testyaku( "*5555pc 111p 999s 3377m 3m!"  ) )
        #print( testyaku( "*5555pc 111p 999s 3377m 3m"  ) )
        #print( testyaku( "*5555pa *111p *999s *777m 3m 3m"  ) )
        #print( testyaku( "*5555pa *111p *999s 3377m 3m"  ) )

if __name__ == "__main__":
    from pprint import pprint
    try:
        unittest.main()
    except:
        pass
