# -*- coding : uft8 -*-

from .agari import *
from .util import *
from .config import *

import numpy as np
import functools,itertools
import collections

YAKU_CHINESE = True

class Yaku:
    def __init__(self,name,cname,score,override=[],bonus=False,multiple=False):
        self.name = name
        self.chinese_name = cname
        self.score = score
        self.override = set( override )
        self.bonus = bonus
        self.multiple = multiple
    def __repr__(self):
        if YAKU_CHINESE :
            return "( {0} : {1} pts. )".format(self.chinese_name,self.score)
        else:
            return "( {0} : {1} pts. )".format(self.name,self.score)
    def toJSON(self):
        return {"name":self.name,"chinese_name":self.chinese_name,"score":self.score}

def topologicalSort(yakus):
    overrided = set()
    yakus = sorted( yakus , key=lambda x:x.score , reverse = True )
    res = []
    for y in yakus : 
        if not ( y in overrided ) :
            overrided |= set(y.override)
            res.append(y) 
    return res
    
# CHINESE DEFAULT SET

def safe_get(dic,key,default=None):
    if key in dic  :
        return dic[key]
    else:
        return default

def yakuroutine(x):
    x.__yakuroutine__ = True
    return x

#オーバーライドテーブルを推移的にする
def override_transitive(cls):
    li = cls.get_yakus()
    f = True
    while f :
        f = False
        for x in li :
            for y in x.override :
                q = x.override | y.override
                if q != x.override :
                    x.override = q
                    f = True
    
                    
                


    


tricolor = list(itertools.permutations([0,1,2]))

class ChineseScore:
    # mentu array format
    #
    # mentu[chow:0,pong:1][color:man,pin,sou,ji][number:1~9]
    #
    #
    #
    @classmethod
    def get_yakus(cls):
        res = []
        li = list( filter( lambda x: len(x)>0 and x[0]!="_" , dir(cls) ))
        for x in li:
            q = getattr(cls,x)
            if isinstance(q,Yaku):
                res.append(q)
        return res
        
    @classmethod
    def judge(cls,tiles,exposed,env,agari_tile=None):
        import traceback
        if agari_tile == None :
            agari_tile = tiles[-1]
        agaris = is_agari(list_to_array(tiles),exposed_mentu=len(exposed))
        if agaris == None :
            #print(tiles,len(exposed))
            return None
        all_tiles = list(tiles)
        for ex in exposed :
            all_tiles.extend( ex.get_tiles() )
        res = []
        env["__noothermachi__"] = True
        __tmp_tiles = list_to_array(tiles)
        __tmp_tiles[agari_tile] -= 1
        for x in MAIN_TILES :
            if x == agari_tile :
                continue
            __tmp_tiles[x] += 1
            if is_agari(__tmp_tiles,exposed_mentu=len(exposed)) is not None :
                env["__noothermachi__"] = False
                break
            __tmp_tiles[x] -= 1
        env["agari_tile"] = agari_tile
        for ag in agaris:
            env["agari_form"] = ag["type"]
            if ag["type"] == "normal":
                parts = Mentu.from_mentu_array( ag["data"] , atama=ag["atama"] )
                for part in parts:
                    if part.contains(agari_tile) :
                        part.agari_tile = agari_tile
                        mentu = list(exposed) + list(parts)
                        res.append( cls.list_yaku(ag["type"],all_tiles,mentu,env) )
                        part.agari_tile = None
            elif ag["type"] == "knitted_normal":
                parts = Mentu.from_mentu_array( ag["data"] , atama=ag["atama"])
                for part in parts:
                    if part.contains(agari_tile) :
                        part.agari_tile = agari_tile
                        mentu = list(exposed) + list(parts)
                        res.append( cls.list_yaku(ag["type"],all_tiles,mentu,env) )
                        part.agari_tile = None
            else:
                res.append( cls.list_yaku(ag["type"],all_tiles,[],env) )
        try:
            res.sort( key = lambda dat:dat[0] , reverse=True )
            res[0][1].sort( key = lambda x:(x.score,x.chinese_name) , reverse = True )
            return res[0]
        except:
            print("exception on **JUDGE**")
            traceback.print_exc()
            return None
    """
    chicken = Yaku( "Chicken Hand" , "無番和" , 8  )
    """
    @classmethod
    def list_yaku(cls,type,tiles,mentu,env):
        obj = cls()
        obj.type = type
        obj.mentu = mentu
        obj.conc_mentu = []
        obj.atama = None
        obj.chows = np.zeros( (4,16) , dtype = np.int16 )
        obj.pongs = np.zeros( (4,16) , dtype = np.int16 )
        obj.cpongs = np.zeros( (4,16) , dtype = np.int16 )
        for x in mentu :
            if x.type == Mentu.ATAMA :
                obj.atama = x.head
                continue
            if x.is_concealed():
                obj.conc_mentu.append(x)
            if x.is_chow() :
                obj.chows[x.get_color(),x.get_number()] += 1
            if x.is_pongorkong() :
                obj.pongs[x.get_color(),x.get_number()] += 1
                if x.is_concealed():
                    obj.cpongs[x.get_color(),x.get_number()] += 1
        obj.tiles = tiles
        obj.env = env
        obj.agari_tile = env["agari_tile"]

        result = []
        li = list( filter( lambda x: len(x)>0 and x[0]!="_" , dir(cls) ))
        for x in li:
            q = getattr(obj,x)
            if hasattr(q,"__yakuroutine__"):
                res = q()
                if res is None:
                    continue
                if isinstance(res, collections.Iterable) :
                    result.extend(res)
                else:
                    result.append(res)
        if len(result) == 0:
            result.append(ChineseScore.chicken)
        result = topologicalSort(result)
        total = np.sum( list(map(lambda x:x.score,result)) )
        total2 = np.sum( list(map(lambda x:x.score if not x.bonus else 0,result)) )
        return (total,result,total2)
    """
    flowerbonus      = Yaku( "Flower" , "花牌" , 1  )
    """
    @yakuroutine
    def f_flowers(self):
        for i in range(safe_get(self.env,"flowers",0)):
            yield flowerbonus

    """
    machi_tanki   = Yaku( "Single Wait" , "単調将" ,  1  )
    machi_closed  = Yaku( "Closed Wait" , "坎張" ,  1  )
    machi_edge    = Yaku( "Edge Wait" , "辺張" ,  1  )
    """
    @yakuroutine
    def f_machi(self):
        if not safe_get(self.env,"__noothermachi__",False):
            return None
        for part in self.mentu:
            q = part.machi()
            if q is not None :
                if q == "KANCHAN":
                    return ChineseScore.machi_closed
                elif q == "PENCHAN":
                    return ChineseScore.machi_edge
                elif q == "TANKI":
                    return ChineseScore.machi_tanki
                else:
                    return None
    """
    pong_t_or_h      = Yaku( "Pong Of Terminals/Honors" , "么九刻" , 1  )
    """
    @yakuroutine
    def f_pong_t_or_h(self):
        c = np.sum( self.pongs[0:3,[1,9]] ) +  np.sum( self.pongs[3,1:5] )
        pw = safe_get(self.env,"prevalent_wind",-1)
        sw = safe_get(self.env,"seat_wind",-1)
        chpongs = self.pongs[3,1:]
        if chpongs[pw] > 0 :
            c-=1
        if chpongs[sw] > 0 :
            c-=1
        for i in range(c):
            yield ChineseScore.pong_t_or_h
    """
    outside          = Yaku( "Outside Hand" , "全帯么" , 4  )
    all_fives        = Yaku( "All Fives" , "全帯五" , 16 , override=[] )
    """
    @yakuroutine
    def f_have(self):
        if self.type != "normal" :
            return None
        yaoset = set( list(YAOCHU) )
        fiveset = set([5,16+5,32+5])
        f5,fy = True,True
        for x in self.mentu:
            t = set( x.get_tiles() )
            if len( t & yaoset ) == 0 :
                fy = False
            if len( t & fiveset ) == 0:
                f5 = False
        if f5 :
            return ChineseScore.all_fives
        if fy :
            return ChineseScore.outside

    """
    onevoid          = Yaku( "One Voided Suit" , "缺一門" , 1  )
    halfflush        = Yaku( "Half Flush" , "混一色" , 6  )
    fullflush        = Yaku( "Full Flush" , "清一色" , 24  )
    alltypes         = Yaku( "All Types" , "五門斉" , 6  )
    """
    @yakuroutine
    def f_types(self):
        typelist = np.zeros(5,dtype=np.bool)
        for t in self.tiles:
            s = id2suit(t)
            if s <= 2:
                typelist[s] = True
            else:
                if id2number(t) <= 4:
                    typelist[3] = True
                else:
                    typelist[4] = True
        if ( typelist ).all() :
            return ChineseScore.alltypes
        elif sum( typelist ) == 1:
            return ChineseScore.fullflush
        elif sum( typelist[0:3] ) == 1:
            return ChineseScore.halfflush
        elif sum( typelist[0:3] ) <= 2 :
            return ChineseScore.onevoid
    """
    four             = Yaku( "Tile Hog" , "四帰一" , 2  )
    """
    @yakuroutine
    def f_four(self):
        fq = list_to_array(self.tiles)
        kongs = list( map( lambda x:x.head , filter( lambda x:x.is_kong(), self.mentu ) ) )
        fours = ( fq >= 4 )
        fours[kongs] = False
        for i in range(np.sum(fours)):
            yield ChineseScore.four
    """
    knit = Yaku( "Lesser Honors And Knitted Tiles" , "全不靠" , 12  )
    knit7 = Yaku( "Greater Honors And Knitted Tiles" , "七星不靠" , 24  )
    """
    @yakuroutine
    def f_knit(self):
        if self.type == "knitted" :
            fq = list_to_array(self.tiles)
            if all( fq[49:49+7] == 1 ) :
                return ChineseScore.knit7
            else:
                return ChineseScore.knit
    """
    ninegates = Yaku( "Nine Gates" , "九連宝燈" , 88 , override=[] )
    """
    @yakuroutine
    def f_nine_gates(self):
        if len(self.conc_mentu)>=4 :
            suit = id2suit( self.tiles[0] )
            if np.all( np.fromiter(map(id2suit,self.tiles),dtype=np.int) == suit ):
                 nums = np.bincount( np.fromiter(map(id2number,self.tiles),dtype=np.int) , minlength=10)
                 nums[id2number(self.agari_tile)] -= 1
                 if np.all( nums - [0,3,1,1,1,1,1,1,1,3] == 0 ):
                     return ChineseScore.ninegates
    """
    termchowsp = Yaku( "Pure Terminal Chows" , "一色双龍会" , 64  )
    termchowsm = Yaku( "Three-Suited Terminal Chows" , "三色双龍会" , 16  )
    """
    @yakuroutine
    def termchows(self):
        atama = self.atama
        if atama is None :
            return None
        if not ( id2suit(atama) <=2 and id2number(atama) == 5 ) :
            return None
        if np.all( self.chows[id2suit(atama),[1,9]] == 2 ) :
            return ChineseScore.termchowsp
        for c in range(3):
            if c == id2suit(atama) :
                if np.all( self.chows[c,[1,9]] == 1 ):
                    pass
                else:
                    return None
        return ChineseScore.termchowsm
    """
    sevenpairs  = Yaku( "Seven Pairs" , "七対" , 24  )
    sevenpairsh = Yaku( "Seven Shifted Pairs" , "連七対" , 88  )
    """
    @yakuroutine
    def f_sevenpairs(self):
        if self.type == "7pairs" :
            fq = list_to_array(self.tiles)
            ini = [1,2,3,17,18,19,33,34,35]
            for x in ini:
                if np.all( fq[x:x+7] == 2 ) :
                    return ChineseScore.sevenpairsh
            return ChineseScore.sevenpairs

    """
    lasttile = Yaku( "Last Tile" , "和絶張" , 4  )
    lastdraw  = Yaku( "Last Tile Draw" , "妙手回春" , 8  ) #
    lastclaim = Yaku( "Last Tile Claim" , "海底撈月" , 8  ) #
    repltile = Yaku( "Out With Replacement Tile" , "槓上開花" , 8  )#
    robkong = Yaku( "Robbing The Kongs" , "搶槓和" , 8  )
    """
    @yakuroutine
    def state_yaku(self):
        open_tiles = []
        open_tiles.extend( safe_get(self.env,"discarded_tiles",[]) )
        open_tiles.extend( safe_get(self.env,"exposed_tiles",[]) )
        open_tiles = np.array(open_tiles)
        if np.sum( open_tiles == self.agari_tile ) >= 3 :
            yield ChineseScore.lasttile

        if safe_get(self.env, "deck_left", -1) == 0:
            if safe_get(self.env,"tsumo",False) :
                yield ChineseScore.lastdraw
            else:
                yield ChineseScore.lastclaim
        if safe_get(self.env,"konged_tile",False) :
            yield ChineseScore.repltile
        if safe_get(self.env,"robbed_tile",False) :
            yield ChineseScore.robkong

    """
    purest = Yaku("Pure Straight","清龍",16)
    knittedst = Yaku("Knitted Straight","組合龍",12)
    mixedst = Yaku("Mixed Straight","花龍",8)
    """
    @yakuroutine
    def straight(self):
        if self.env["agari_form"] != "normal":
            if self.env["agari_form"] == "knitted_normal":
                return ChineseScore.knittedst
            elif self.env["agari_form"] == "knitted" :
                if len(list(filter(lambda x:id2suit(x)<=2,self.tiles))) == 9:
                    return ChineseScore.knittedst
            return None
        chows = self.chows
        pure = np.all( chows[:,[1,4,7]]>0 , axis=1).any()
        if pure :
            return ChineseScore.purest
        for r in tricolor:
            if chows[0,1+r[0]*3] > 0 and chows[1,1+r[1]*3] > 0 and chows[2,1+r[2]*3] > 0:
                return ChineseScore.mixedst
    """
    kong4  = Yaku("4 Kongs","四槓",88)#
    kong3  = Yaku("3 Kongs","三槓",32)#
    kong2c = Yaku("2 Concealed Kongs","双暗槓",8)#
    kong2  = Yaku("2 Kongs","双明槓",4)#
    kong1c = Yaku("Concealed Kong","暗槓",2)#
    kong1  = Yaku("Kong","明槓",1)#
    """
    @yakuroutine
    def kongs(self):
        kongs = list( filter( lambda x:x.is_kong(), self.mentu ) )
        conckongs = list( filter( lambda x:x.is_concealed(), kongs ) )
        kl = len(kongs)
        ckl = len(conckongs)
        res = []

        if ckl >= 2:
            res.append(ChineseScore.kong2c)
        elif ckl >= 1:
            res.append(ChineseScore.kong1c)

        if kl >= 4:
            res.append(ChineseScore.kong4)
        elif kl >= 3 :
            res.append(ChineseScore.kong3)
        elif kl >= 2 :
            res.append(ChineseScore.kong2)       
        elif kl >= 1 :
            res.append(ChineseScore.kong1)
        return res
    """
    menzen           = Yaku( "Concealed Hand" , "門前清" ,  2  )
    selfdrawn        = Yaku( "Self Drawn" , "自摸" ,  1  )
    menzentsumo      = Yaku( "Fully Concealed" , "不求人" ,  4  )
    allmeld          = Yaku( "Melded Hand" , "全求人" ,  6  )
    """
    @yakuroutine
    def f_melds(self):
        melded_m = list(filter(lambda x:(not x.is_concealed() and x.agari_tile == None ) and not x.type==Mentu.ATAMA , self.mentu ))
        meldcnt = len(melded_m)
        meldcnt2 = len(list(filter(lambda x:not x.is_concealed() and not x.type==Mentu.ATAMA and x.agari_tile == None , self.mentu )))
        if safe_get(self.env,"tsumo",False) :
            if meldcnt == 0:
                return ChineseScore.menzentsumo
            else:
                return ChineseScore.tsumo
        else:
            if meldcnt2 == 4:
                return ChineseScore.allmeld
            elif meldcnt == 0:
                return ChineseScore.menzen
    """
    allpong = Yaku("All Pongs","碰碰和",6)#
    allevenpong      = Yaku("All Even Pongs", "全双刻" ,     24  )
    pong4c = Yaku( "4 Concealed Pongs" , "四暗刻" , 64  )#
    pong3c = Yaku( "3 Concealed Pongs" , "三暗刻" , 16  )#
    pong2c = Yaku( "2 Concealed Pongs" , "双暗刻" , 2  )#
    """
    @yakuroutine
    def f_pongs(self):
        pongs = self.pongs
        ts = safe_get(self.env,"tsumo",False) 
        s = sum( [ 1 if m.is_fully_concealed_pong(ts) else 0 for m in self.mentu] )
        if np.sum(pongs) >= 4 :
            if filter( lambda x:id2suit(x)<=2 and (id2number(x)&1)==0 , self.tiles ) == 14 :
                yield ChineseScore.allevenpong
            else:
                yield ChineseScore.allpong
        if s >= 4:
            yield ChineseScore.pong4c
        elif s >= 3 :
            yield ChineseScore.pong3c
        elif s >= 2 :
            yield ChineseScore.pong2c
    """
    step4p   = Yaku( "Four Shifted Chows" , "一色四歩高" , 32  )#
    step3p   = Yaku( "Three Shifted Chows" , "一色三歩高" , 16  )#
    step3mp  = Yaku( "Mixed Shifted Chows" , "三色三歩高" , 6  )#
    """
    @yakuroutine
    def f_steps(self):
        chows = self.chows
        for c in range(3):
            for i in range(1,6):
                if chows[c,i] == 0 :
                    continue
                if chows[c,i+1] > 0 and chows[c,i+2] > 0 :
                    if chows[c,i+3]>0 :
                        return ChineseScore.step4p
                    else:
                        return ChineseScore.step3p
                if chows[c,i+2] > 0 and chows[c,i+4] > 0 :
                    if chows[c,i+6]>0 :
                        return ChineseScore.step4p
                    else:
                        return ChineseScore.step3p
        for r in tricolor:
            for i in range(10):
                if chows[0,i+r[0]] > 0 and chows[1,i+r[1]] > 0 and chows[2,i+r[2]] > 0:
                    return ChineseScore.step3mp
        return None
    """
    pong4sh  = Yaku( "Four Pure Shifted Pongs" , "一色四節高" , 48  )#
    pong3sh  = Yaku( "Triple Pure Shifted Pongs" , "一色三節高" , 24  )#
    pong3msh = Yaku( "Mixed Shifted Pongs" , "三色三節高" , 6  )#
    """
    @yakuroutine
    def shifted(self):
        pongs = self.pongs
        for c in range(3):
            for i in range(1,8):
                if pongs[c,i] == 0 :
                    continue
                if pongs[c,i+1] > 0 and pongs[c,i+2] > 0 :
                    if pongs[c,i+3]>0 :
                        return ChineseScore.pong4sh
                    else:
                        return ChineseScore.pong3sh
        for r in tricolor:
            for i in range(9):
                if pongs[0,i+r[0]] > 0 and pongs[1,i+r[1]] > 0 and pongs[2,i+r[2]] > 0:
                    return ChineseScore.pong3msh
        return None

    """
    pong3s = Yaku( "Triple Pong" , "三同刻" , 16  )#
    pong2s = Yaku( "Double Pong" , "双同刻" , 2  )#
    """
    @yakuroutine
    def samepong(self):
        cnt = np.sum( self.pongs[0:3] > 0 , axis = 0 )
        if ( cnt >= 3 ).any() :
            return ChineseScore.pong3s
        if ( cnt >= 2 ).any() :
            return ChineseScore.pong2s
    """
    chow4s   = Yaku( "Quadruple Chow" , "一色四同順" , 48  )#
    chow3s   = Yaku( "Pure Triple Chow" , "一色三同順" , 24  )#
    chow3ms  = Yaku( "Mixed Triple Chow" , "三色三同順" , 8  )#
    """
    @yakuroutine
    def samechow(self):
        cnt = self.chows
        if ( cnt >= 4 ).any():
            return ChineseScore.chow4s
        if ( cnt >= 3 ).any():
            return ChineseScore.chow3s
        mcnt = np.all( self.chows[0:3,:] > 0 , axis = 0 )
        if ( mcnt ).any() :
            return ChineseScore.chow3ms

    """
    wind4  = Yaku("Big Four Kongs","大四喜",88)
    wind4s = Yaku("Little Four Kongs","小四喜",64)
    wind3  = Yaku("Three Winds","三風刻",12)
    prev_wind = Yaku( "Prevalent Wind" , "圏風刻" , 2  )
    seat_wind  = Yaku( "Seat Wind" , "門風刻" , 2  )
    dragon3  = Yaku("Big Three Dragons","大三元",88)
    dragon3s = Yaku("Little Three Dragons","小三元",64)
    dragon2  = Yaku("Two Dragons","双箭刻",6)
    dragon1  = Yaku("Dragon Pong","箭刻",2)
    """
    @yakuroutine
    def winds_and_dragons(self):
        chpongs = self.pongs[3,1:]
        pw = safe_get(self.env,"prevalent_wind",-1)
        sw = safe_get(self.env,"seat_wind",-1)
        atama = list(filter( lambda x:x.type == Mentu.ATAMA , self.mentu ))
        if len(atama) > 0:
            atama = atama[0].head
        else:
            atama = -1
        if ( chpongs[0:4] > 0 ).all():
            return ChineseScore.wind4
        if np.sum( chpongs[0:4] > 0 ) >= 3 :
            if 49 <= atama < 49 + 4 :
                yield ChineseScore.wind4s
            else:
                yield ChineseScore.wind3
        dragons = np.sum( chpongs[4:7] > 0 )
        if dragons >= 3 :
            yield ChineseScore.dragon3
        elif dragons >= 2 :
            if 53 <= atama < 53 + 3 :
                yield ChineseScore.dragon3s
            else:
                yield ChineseScore.dragon2
        elif dragons >= 1:
            yield ChineseScore.dragon1

        if chpongs[pw] > 0 :
            yield ChineseScore.prev_wind
        if chpongs[sw] > 0 :
            yield ChineseScore.seat_wind
    """
    chow2m           = Yaku( "Mixed Double Chow" , "喜相逢" , 1  )#
    chow2p           = Yaku( "Pure Double Chow" , "一般高" , 1  )#
    six              = Yaku( "Short Straight" , "連六" , 1  )#
    twoterms         = Yaku( "Two Terminal Chows" , "老少副" , 1  )#
    """
    @yakuroutine
    def twochows(self):
        chows = self.chows
        ipp = np.sum(chows >= 2)
        kso = np.sum( ( np.sum(chows,axis=0) - np.max(chows,axis=0) ) > 0 )
        rsf = np.sum( np.min( chows[ : , [1,7] ] , axis=1 ) > 0 )
        sx = np.sum( np.minimum( chows[:,1:5] , chows[:,4:8] ) > 0 )
        doubled = False
        if ipp > 0:
            yield ChineseScore.chow2p
            if ipp >= 2 and not doubled :
                doubled = True
                yield ChineseScore.chow2p
        if kso > 0:
            yield ChineseScore.chow2m
            if kso >= 2 and not doubled :
                doubled = True
                yield ChineseScore.chow2m
        if rsf > 0:
            yield ChineseScore.twoterms
            if rsf >= 2 and not doubled :
                doubled = True
                yield ChineseScore.twoterms
        if sx > 0:
            yield ChineseScore.six
            if sx >= 2 and not doubled :
                doubled = True
                yield ChineseScore.six
    """
    allchow = Yaku("All Chows","平和",2)
    no_honor         = Yaku( "No Honor" , "無字" , 1  )
    all_simples      = Yaku( "All Simples" , "断么" ,  2  )
    upp4 = Yaku( "Upper Four" , "大于五" ,      12  )
    low4 = Yaku( "Lower Four" , "小于五" ,     12  )
    upp3 = Yaku( "All Upper Tiles" ,  "全大" ,   24  )
    mid3 = Yaku( "All Middle Tiles" ,  "全中" ,  24  )
    low3 = Yaku( "All Lower Tiles" , "全小" , 24 )
    allgreen = Yaku( "All Green" , "緑一色" , 88 )
    allsymm = Yaku( "Reversible Tiles" , "推不倒" , 8 )
    all_t_or_h = Yaku( "All Terminals/Honors" , "混么九" , 32  )
    allhonor = Yaku( "All Honors" , "字一色" ,        64  )
    allterm = Yaku( "All Terminals" , "清么九" ,     64  )
    orphans13 = Yaku( "Thirteen Orphans" , "十三么" , 88  )
    """
    @yakuroutine
    def contain(self):
        tileset = set(self.tiles)
        if tileset.issubset( set( [ 2,3,4,5,6,7,8, 18,19,20,21,22,23,24 , 34,35,36,37,38,39,40 ] ) ) :
            yield ChineseScore.all_simples
        
        if tileset.issubset( set( [ 1,2,3,4,5,6,7,8,9, 17,18,19,20,21,22,23,24,25 , 33,34,35,36,37,38,39,40,41 ] ) ) :
            if np.sum(self.chows) == 4 or ( self.type == "knitted_normal" and np.sum(self.chows) == 1 ) :
                yield ChineseScore.allchow
            else:
                yield ChineseScore.no_honor



        if tileset.issubset( set( [ 4,5,6, 20,21,22 , 36,37,38 ] ) ) :
            yield ChineseScore.mid3

        if tileset.issubset( set( [ 1,2,3, 17,18,19 , 33,34,35 ] ) ) :
            yield ChineseScore.low3
        elif tileset.issubset( set( [ 1,2,3,4, 17,18,19,20 , 33,34,35,36 ] ) ) :
            yield ChineseScore.low4

        if tileset.issubset( set( [ 7,8,9, 23,24,25 , 39,40,41 ] ) ) :
            yield ChineseScore.upp3
        elif tileset.issubset( set( [ 6,7,8,9, 22,23,24,25 , 38,39,40,41 ] ) ) :
            yield ChineseScore.upp4

        if tileset.issubset( set( [ 34,35,36,38,40,54 ] ) ) :
            yield ChineseScore.allgreen

        if tileset.issubset( set( [ 49,50,51,52,53,54,55 ] ) ) :
            yield ChineseScore.allhonor

        if tileset.issubset( set( [ 1,9,16+1,16+9,32+1,32+9 ] ) ) :
            yield ChineseScore.allterm

        if tileset.issubset( set( [ 1,9,16+1,16+9,32+1,32+9,49,50,51,52,53,54,55 ] ) ) :
            yield ChineseScore.all_t_or_h

    flowerbonus = Yaku("Flower", "花牌", 1)
    machi_tanki = Yaku("Single Wait", "単調将",  1)
    machi_closed = Yaku("Closed Wait", "坎張",  1)
    machi_edge = Yaku("Edge Wait", "辺張",  1)
    chow2m = Yaku("Mixed Double Chow", "喜相逢", 1)
    chow2p = Yaku("Pure Double Chow", "一般高", 1)
    six = Yaku("Short Straight", "連六", 1)
    twoterms = Yaku("Two Terminal Chows", "老少副", 1)
    pong_t_or_h = Yaku("Pong Of Terminals/Honors", "么九刻", 1)
    onevoid = Yaku("One Voided Suit", "缺一門", 1)
    kong1 = Yaku("Kong", "明槓", 1)
    tsumo = Yaku("Self Drawn", "自摸",  1)
    no_honor = Yaku("No Honor", "無字", 1)

    four = Yaku("Tile Hog", "四帰一", 2 )
    kong1c = Yaku("Concealed Kong", "暗槓", 2 , override=[kong1] )
    menzen = Yaku("Concealed Hand", "門前清", 2)
    pong2c = Yaku("2 Concealed Pongs", "双暗刻", 2 )
    pong2s = Yaku("Double Pong", "双同刻", 2)
    prev_wind = Yaku("Prevalent Wind", "圏風刻", 2)
    seat_wind = Yaku("Seat Wind", "門風刻", 2)
    dragon1 = Yaku("Dragon Pong", "箭刻", 2)
    allchow = Yaku("All Chows", "平和", 2,override=[no_honor])
    all_simples = Yaku("All Simples", "断么",  2, override=[no_honor])

    outside = Yaku("Outside Hand", "全帯么", 4 , override=[] )
    lasttile = Yaku("Last Tile", "和絶張", 4 , override=[] )
    kong2 = Yaku("2 Kongs", "双明槓", 4 , override=[kong1] )
    menzentsumo = Yaku("Fully Concealed", "不求人", 4 , override=[menzen,tsumo] )
   
    halfflush = Yaku("Half Flush", "混一色", 6 , override=[onevoid] )
    alltypes = Yaku("All Types", "五門斉", 6 ,override=[])
    allmeld = Yaku("Melded Hand", "全求人", 6 , override=[machi_tanki] )
    allpong = Yaku("All Pongs", "碰碰和", 6 , override=[] )
    step3mp = Yaku("Mixed Shifted Chows", "三色三歩高", 6 , override=[] )
    dragon2 = Yaku("Two Dragons", "双箭刻", 6 ,override=[dragon1]) 

    chicken = Yaku("Chicken Hand", "無番和", 8)
    lastdraw = Yaku("Last Tile Draw", "妙手回春", 8,override=[tsumo])
    lastclaim = Yaku("Last Tile Claim", "海底撈月",8,override=[])
    repltile = Yaku("Out With Replacement Tile", "槓上開花", 8,override=[tsumo])
    robkong = Yaku("Robbing The Kongs", "搶槓和", 8 , override=[lasttile] )
    mixedst = Yaku("Mixed Straight", "花龍", 8 , override=[])
    kong2c = Yaku("2 Concealed Kongs", "双暗槓", 8 ,override=[kong1c,kong2] )
    chow3ms = Yaku("Mixed Triple Chow", "三色三同順", 8 , override=[chow2m] )
    pong3msh = Yaku("Mixed Shifted Pongs", "三色三節高", 8 , override=[] )
    allsymm = Yaku("Reversible Tiles", "推不倒", 8 , override=[onevoid] )

    knittedst = Yaku("Knitted Straight", "組合龍", 12 , override=[] )
    knit = Yaku("Lesser Honors And Knitted Tiles", "全不靠", 12 , override=[menzen,machi_tanki,alltypes])
    wind3 = Yaku("Three Winds", "三風刻", 12 , override=[])
    upp4 = Yaku("Upper Four", "大于五",      12 ,override=[no_honor])
    low4 = Yaku("Lower Four", "小于五",     12,override=[no_honor])

    all_fives = Yaku("All Fives", "全帯五", 16, override=[all_simples])
    termchowsm = Yaku("Three-Suited Terminal Chows",
                      "三色双龍会", 16, override=[twoterms,allchow,chow2m])
    purest = Yaku("Pure Straight", "清龍", 16,override=[six,twoterms])
    pong3c = Yaku("3 Concealed Pongs", "三暗刻", 16,override=[pong2c])
    step3p = Yaku("Three Shifted Chows", "一色三歩高", 16,override=[])
    pong3s = Yaku("Triple Pong", "三同刻", 16 , override=[pong2s])

    fullflush = Yaku("Full Flush", "清一色", 24 , override=[halfflush,no_honor])
    sevenpairs = Yaku("Seven Pairs", "七対", 24 , override=[menzen,machi_tanki] )
    allevenpong = Yaku("All Even Pongs", "全双刻", 24,override=[allpong,all_simples])
    pong3sh = Yaku("Triple Pure Shifted Pongs", "一色三節高", 24 , override=[] )
    chow3s = Yaku("Pure Triple Chow", "一色三同順", 24 , override=[chow2p] )
    knit7 = Yaku("Greater Honors And Knitted Tiles", "七星不靠", 24,override=[knit])
    upp3 = Yaku("All Upper Tiles",  "全大",   24,override=[upp4,no_honor])
    mid3 = Yaku("All Middle Tiles",  "全中",  24, 
                override=[no_honor, all_simples])
    low3 = Yaku("All Lower Tiles", "全小", 24, override=[low4,no_honor])

    kong3 = Yaku("3 Kongs", "三槓", 32 , override=[] )
    all_t_or_h = Yaku("All Terminals/Honors", "混么九", 32,
                override=[allpong, pong_t_or_h, outside])
    step4p = Yaku("Four Shifted Chows", "一色四歩高", 32,override=[onevoid])

    pong4sh = Yaku("Four Pure Shifted Pongs", "一色四節高", 48,override=[onevoid])
    chow4s = Yaku("Quadruple Chow", "一色四同順", 48,override=[onevoid])

    termchowsp = Yaku("Pure Terminal Chows", "一色双龍会",
                      64, override=[fullflush, allchow, twoterms , chow2p ])
    pong4c = Yaku("4 Concealed Pongs", "四暗刻", 64,override=[pong3c,allpong,menzen])
    allhonor = Yaku("All Honors", "字一色",        64,
                override=[pong_t_or_h,halfflush,fullflush,allpong])
    allterm = Yaku("All Terminals", "清么九",     64, override=[all_t_or_h,allpong,no_honor])
    wind4s = Yaku("Little Four Kongs", "小四喜", 64 , override=[wind3,pong_t_or_h,halfflush] )
    dragon3s = Yaku("Little Three Dragons", "小三元", 64 , override=[dragon2])

    kong4 = Yaku("4 Kongs", "四槓", 88,override=[kong3,machi_tanki,allpong])
    sevenpairsh = Yaku("Seven Shifted Pairs", "連七対", 88 , override=[sevenpairs,fullflush,menzen,machi_tanki])
    wind4 = Yaku("Big Four Kongs", "大四喜", 88 , override=[wind3,prev_wind,seat_wind,allpong,pong_t_or_h])
    dragon3 = Yaku("Big Three Dragons", "大三元", 88 , override=[dragon1,dragon2] )
    allgreen = Yaku("All Green", "緑一色", 88 , override=[halfflush])
    orphans13 = Yaku("Thirteen Orphans", "十三么", 88, override=[alltypes,menzen,machi_tanki,all_t_or_h])
    ninegates = Yaku("Nine Gates", "九連宝燈", 88, override=[fullflush,pong_t_or_h,menzen])

override_transitive(ChineseScore)
#print( list( filter( lambda x: len(x)>0 and x[0]!="_" , dir(ChineseScore) )) )
# sc = ScoreCalculation(checker=ChineseScore)
# print(len( sc.yaku ))
# print( ",".join( map( lambda x: x.chinese_name , sc.yaku ) ) )



"""
            "prevalent_wind": game.prevalent_wind ,
            "seat_wind": game.get_seat_wind(self.id),
            "tsumo":tsumo ,
            "agari_tile":tile,
            "deck_left":game.lefttile(),
            "discarded_tiles": [ self.trash for p in game.players ],
            "exposed_tiles": [ self.exposed for p in game.players ]
"""


#    


    #print(TestScore.__sc__.calc_score(getmentu("123m234p345sEEESS") ) )
    #print(TestScore.__sc__.calc_score(getmentu("123m456p123789sSS") ) )
    #print(TestScore.__sc__.calc_score(getmentu("123789123789mWW") ) )
    #print( string_to_list_ex("67m 123456789s 99p 5m!") )
    #print( string_to_list_ex("*456p *789m *567s 5678p 5p") )
    #print( string_to_list_ex("*SSS *777s *111m 888s H H!") )
    
    #print( testyaku( "*5555pk *111p *999s 3377m 3m"  ) )
    #print( testyaku( "*5555pc 111p 999s 3377m 3m!"  ) )
    #print( testyaku( "*5555pc 111p 999s 3377m 3m"  ) )
    #print( testyaku( "*5555pa *111p *999s *777m 3m 3m"  ) )
    #print( testyaku( "*5555pa *111p *999s 3377m 3m"  ) )

    #print(ChineseScore.get_yakus())
    #print(len(ChineseScore.get_yakus()))
    #print( testyaku( "1122335566778m 8m!"  ) )
    #print( testyaku( "WWW EEE SSS 111m 99s" ) )
    # print( testyaku( "*333s *678m 555p WWGG W" ) ) 7pts
