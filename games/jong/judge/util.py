

import numpy as np
import functools
import itertools


class Mentu:
    CHOW = 1
    PUNG = 2
    MINKONG = 3
    APKONG = 4
    CONCKONG = 5
    CONCCHOW = 6
    CONCPUNG = 7
    ATAMA = 8
    __TYPENAMES__ = ["","chow","pong","minkong","conckong","apkong","concchow","concpung","atama"]

    def get_melded_type(self):
        if self.type == self.__class__.CONCCHOW :
            return Mentu.CHOW
        elif self.type == self.__class__.CONCPUNG :
            return Mentu.PUNG
        else:
            return self.type

    def __init__(self,type,head,agari_tile=None):
        self.type = type
        self.head = head
        self.agari_tile = agari_tile

    def __repr__(self):
        if self.type == self.__class__.CHOW :
            return "CHOW( %d,%d,%d )" % (self.head,self.head+1,self.head+2)
        elif self.type == self.__class__.PUNG :
            return "PUNG( %d,%d,%d )" % (self.head,self.head,self.head)
        elif self.type == self.__class__.MINKONG :
            return "MINKONG( %d,%d,%d,%d )" % (self.head,self.head,self.head,self.head)
        elif self.type == self.__class__.APKONG :
            return "APKONG( %d,%d,%d,%d )" % (self.head,self.head,self.head,self.head)
        elif self.type == self.__class__.CONCKONG :
            return "CONCKONG( %d,%d,%d,%d )" % (self.head,self.head,self.head,self.head)
        elif self.type == self.__class__.CONCCHOW :
            return "CONCCHOW( %d,%d,%d )" % (self.head,self.head+1,self.head+2)
        elif self.type == self.__class__.CONCPUNG :
            return "CONCPUNG( %d,%d,%d )" % (self.head,self.head,self.head)
        elif self.type == self.__class__.ATAMA :
            return "ATAMA( %d,%d )" % (self.head,self.head)

    def get_tiles(self):
        if self.type == self.__class__.CHOW or self.type == self.__class__.CONCCHOW :
            return (self.head,self.head+1,self.head+2)
        elif self.type == self.__class__.PUNG or self.type == self.__class__.CONCPUNG :
            return (self.head,self.head,self.head)
        elif self.type == self.__class__.MINKONG or self.type == self.__class__.APKONG or self.type == self.__class__.CONCKONG :
            return (self.head,self.head,self.head,self.head)
        elif self.type == self.__class__.ATAMA :
            return (self.head,self.head)

    def contains(self,x):
        if self.type == self.__class__.CHOW or self.type == self.__class__.CONCCHOW :
            return self.head <= x <= self.head+2
        else:
            return x == self.head

    def machi(self): # machi type for 1 pts hands
        if self.agari_tile is None :
            return None
        if self.type == self.__class__.CHOW or self.type == self.__class__.CONCCHOW :
            if self.agari_tile == self.head + 1 :
                return "KANCHAN"
            elif self.agari_tile == self.head and id2number(self.head) == 7 :
                return "PENCHAN"
            elif self.agari_tile == self.head + 2 and id2number(self.head) == 1 :
                return "PENCHAN"
            else:
                return "OTHER1"
        elif self.type == self.__class__.ATAMA :
            return "TANKI"
        else:
            return "OTHER2"

    @classmethod
    def from_mentu_array(cls,data,atama=None):
        nzs = data.nonzero()
        res = []
        if atama is not None:
            res.append( cls( cls.ATAMA , atama ) )
        types , suits , nums = nzs
        for j in range(len(nums)) :
            type , suit , num = types[j] , suits[j] , nums[j]
            for i in range( data[type,suit,num] ):
                res.append( cls( 7 - type  , suit * 16 + num ) )
        return res


    def toDict(self):
        return {"type":self.__class__.__TYPENAMES__[self.type] , "tiles":self.get_tiles() }

    def mentu_id(self):
        return self.head

    def is_kong(self):
        return self.type == self.__class__.MINKONG or self.type == self.__class__.CONCKONG or self.type == self.__class__.APKONG

    def is_pong(self):
        return self.type == self.__class__.PUNG or self.type == self.__class__.CONCPUNG

    def is_chow(self):
        return self.type == self.__class__.CHOW or self.type == self.__class__.CONCCHOW

    def is_pongorkong(self):
        return self.is_pong() or self.is_kong()

    def is_conc_pongorkong(self):
        return ( self.is_pong() or self.is_kong() ) and self.is_concealed()

    def is_fully_concealed_pong(self,tsumo):
        if tsumo :
            return self.is_conc_pongorkong()
        return self.is_conc_pongorkong() and self.agari_tile == None

    def is_concealed(self):
        return self.type == self.__class__.CONCKONG or self.type == self.__class__.CONCCHOW or self.type == self.__class__.CONCPUNG

    def get_color(self):
        return self.head // 16

    def get_number(self):
        return self.head % 16

    def toJSON(self):
        return self.toDict()



YAOCHU = [1,9,16+1,16+9,32+1,32+9,49,50,51,52,53,54,55]
YAOCHU_NUM = [1,9,16+1,16+9,32+1,32+9]

MAIN_TILES = [1,2,3,4,5,6,7,8,9,
        17,18,19,20,21,22,23,24,25,
        33,34,35,36,37,38,39,40,41,
        49,50,51,52,53,54,55]

def id2number(t):
    return t%16

def id2suit(t):
    return t//16

def list_to_array(li):
    res = np.zeros(64  ,dtype=np.int16)
    for x in li:
        res[x] += 1
    return res

def list_to_string(li):
    li = sorted(li)
    m = ""
    p = ""
    s = ""
    c = ""
    cname = " ESWNHGR"
    for x in li:
        if 1 <= x <= 9 :
            m = m + str(x)
        elif 1 <= (x-16) <= 9 :
            p = p + str(x-16)
        elif 1 <= (x-32) <= 9 :
            s = s + str(x-32)
        elif 1 <= (x-48) <= 9 :
            c = c + cname[x-48]
    res = ""
    if m != "" :
        res += m+"m"
    if p != "" :
        res += p+"p"
    if s != "" :
        res += s+"s"
    res += c
    return res

def __parse_string_to_list_ex(s):
    res = []
    mentu_res = []
    tsumo = False

    buff = []
    mentu_buff = ""
    mode = 0
    d = { "E":49 , "S" : 50 , "W":51 , "N":52,"H":53,"G":54,"R":55 }
    kong_type_tbl = {"k":Mentu.MINKONG,"a":Mentu.APKONG,"c":Mentu.CONCKONG}
    for c in s:
        if mode == 0 : # normal
            if '0' <= c <= '9':
                buff.append(int(c))
            elif c == "m" :
                res.extend( map(lambda x:x,buff) )
                buff=[]
            elif c == "p" :
                res.extend( map(lambda x:x+16,buff) )
                buff=[]
            elif c == "s" :
                res.extend( map(lambda x:x+32,buff) )
                buff=[]
            elif c in d :
                res.append(d[c])
            elif c == "*":
                mode = 1
            elif c == "!":
                tsumo = True
            else :
                pass
        elif mode == 1 :
            if c != " " and c != "*" :
                mentu_buff += c
            else:
                if mentu_buff[-1] in ["k","a","c"] :
                    kong_type = kong_type_tbl[mentu_buff[-1]]
                    mentu_buff = mentu_buff[0:-1]
                rm = string_to_list(mentu_buff)
                tiles = sorted(rm)
                if len(tiles) == 4 :
                    if tiles[0] == tiles[1] and tiles[0] == tiles[2] and tiles[0] == tiles[3] :
                        mentu_obj = Mentu(kong_type,tiles[0])
                elif len(tiles) == 3 :
                    if tiles[0] == tiles[1] and tiles[0] == tiles[2] :
                        mentu_obj = Mentu(Mentu.PUNG,tiles[0])
                    if tiles[0]+1 == tiles[1] and tiles[0]+2 == tiles[2] :
                        mentu_obj = Mentu(Mentu.CHOW,tiles[0])
                else:
                    raise SyntaxError()
                mentu_res.append(mentu_obj)
                mentu_buff = ""
                mode = 0
    return res,mentu_res,tsumo

def string_to_list_ex(s):
    res = __parse_string_to_list_ex(s)
    return res

def string_to_list(s):
    res = []
    buff = []
    d = { "E":49 , "S" : 50 , "W":51 , "N":52,"H":53,"G":54,"R":55 }
    for c in s:
        if '0' <= c <= '9':
            buff.append(int(c))
        elif c == "m" :
            res.extend( map(lambda x:x,buff) )
            buff=[]

        elif c == "p" :
            res.extend( map(lambda x:x+16,buff) )
            buff=[]

        elif c == "s" :
            res.extend( map(lambda x:x+32,buff) )
            buff=[]

        else:
            res.append(d[c])
    return res

def string_to_array(s):
    return list_to_array(string_to_list(s))


BITS = np.array( [1<<i for i in range(16)] )

def to_bits(ary):
    aa = np.array(ary)
    aa[aa.nonzero()] = 1
    print(ary,aa)
    return np.sum( aa * BITS[0:len(aa)] )

def from_bits(bits):
    aa = np.zeros(16,dtype=np.int16)
    for i in range(16):
        aa[i] = ( bits >> i ) & 1
    return aa

def randomhand(length=14):
    deck = np.array( [1,2,3,4,5,6,7,8,9,
            17,18,19,20,21,22,23,24,25,
            33,34,35,36,37,38,39,40,41,
            49,50,51,52,53,54,55] * 4 ) # + [56] * 8 )
    np.random.shuffle(deck)
    return np.bincount(deck[0:length],minlength=64)



def to_array(man="",pin="",sou="",ji=""):
    res = np.zeros(64,dtype=np.int16)
    for c in man:
        res[int(c)]+=1
    for c in pin:
        res[int(c)+16]+=1
    for c in sou:
        res[int(c)+32]+=1
    # "eswnhrg"
    for c in ji:
        res[int(c)+48]+=1
    return res

KNITS = np.zeros( (6,64) ,dtype=np.int16 )
KNITMASK = np.zeros( (6,64) ,dtype=np.int16 )
KNITNUMS = np.zeros( (6,16) ,dtype=np.int16 )
def _init_knit():
    m1 = ( 1 | 1 << 3 | 1 << 6 ) << 1
    m2 = m1<<1
    m3 = m1<<2
    for i,v in enumerate(itertools.permutations( ( m1 , m2 , m3 ) )) :
        a , b , c = v
        KNITS[i,0:16] = from_bits(a)
        KNITS[i,16:32] = from_bits(b)
        KNITS[i,32:48] = from_bits(c)
        KNITMASK[i,0:16] += from_bits(a)
        KNITMASK[i,16:32] += from_bits(b)
        KNITMASK[i,32:48] += from_bits(c)
        KNITMASK[i,49:49+7] += 1
        KNITNUMS[i,:] = (KNITMASK[i]).nonzero()[0]
_init_knit()

if __name__ == "__main__" :
    print( string_to_list_ex("67m 123456789s 99p 5m!") )
    print( string_to_list_ex("*456p *789m *567s 5678p 5p") )
    print( string_to_list_ex("*SSS *777s *111m 888s H H!") )
