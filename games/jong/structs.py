

from functools import total_ordering

@total_ordering
class Claim:
    SKIP = 0
    CHOW = 1
    PUNG = 2
    MINKONG = 3
    RON = 4
    __TYPENAMES__ = ["SKIP","CHOW","PONG","KONG","RON"]
    def __init__(self,type=0,pos=0):
        self.type = type
        self.pos = pos

    def __eq__(self,other):
        return (self.type==other.type) and (self.pos==other.pos)

    def __lt__(self,other):
        return (self.type<other.type) or ( (self.type==other.type) and (self.pos<other.pos) )

    def __str__(self):
        return "%s : %s" % ( self.__class__.__TYPENAMES__[self.type],str(self.pos))

    def __repr__(self):
        return "Claim( %s : %s)" % ( self.__class__.__TYPENAMES__[self.type],repr(self.pos))

    def toJSON(self):
        return self.toDict()

    @classmethod
    def fromDict(cls,value):
        type = value["type"].upper()
        if "pos" in value :
            pos = value["pos"]
            if isinstance(pos,list) :
                pos = list(map(int,pos))
            else:
                pos = int( pos )
        tid = -1
        for (k,v) in enumerate( cls.__TYPENAMES__ ) :
            if v == type :
                tid = k
                break
        return cls(tid,pos)

    def toDict(self):
        return { "type" :  self.__class__.__TYPENAMES__[self.type].lower() , "pos" : self.pos }



class TurnCommand:
    DISCARD = 1
    APKONG = 2
    CONCKONG = 3
    TSUMO = 4
    __TYPENAMES__ = ["","DISCARD","APKONG","CONCKONG","TSUMO"]
    def __init__(self,type=0,pos=0,target=None):
        self.type = type
        self.pos = pos
        self.target = target

    def __eq__(self,other):
        return (self.type==other.type) and (self.pos==other.pos)

    def __lt__(self,other):
        return (self.type<other.type) or ( (self.type==other.type) and (self.pos<other.pos) )

    def __str__(self):
        return "%s : %s" % (self.__class__.__TYPENAMES__[self.type],str(self.pos))

    def __repr__(self):
        return "TurnCommand( %s : %s)" % ( self.__class__.__TYPENAMES__[self.type],repr(self.pos))


    def toJSON(self):
        return self.toDict()

    @classmethod
    def fromDict(cls,value):
        type = value["type"].upper()
        if "pos" in value :
            pos = value["pos"]
            if isinstance(pos,list) :
                pos = list(map(int,pos))
            else:
                pos = int( pos )
        tid = -1
        for (k,v) in enumerate( cls.__TYPENAMES__ ) :
            if v == type :
                tid = k
                break
        return cls(tid,pos)

    def toDict(self):
        return { "type" : self.__class__.__TYPENAMES__[self.type].lower() , "pos" : self.pos , "target" : self.target }

class Exposed:
    CHOW = 1
    PUNG = 2
    MINKONG = 3
    APKONG = 4
    CONCKONG = 5
    __TYPENAMES__ = ["","chow","pong","minkong","apkong","conckong"]
    def __init__(self,type,head):
        self.type = type
        self.head = head

    def __repr__(self):
        if self.type == Exposed.CHOW :
            return "CHOW( %d,%d,%d )" % (self.head,self.head+1,self.head+2)
        elif self.type == Exposed.PUNG :
            return "PUNG( %d,%d,%d )" % (self.head,self.head,self.head)
        elif self.type == Exposed.MINKONG :
            return "MINKONG( %d,%d,%d,%d )" % (self.head,self.head,self.head,self.head)
        elif self.type == Exposed.APKONG :
            return "APKONG( %d,%d,%d,%d )" % (self.head,self.head,self.head,self.head)
        elif self.type == Exposed.CONCKONG :
            return "CONCKONG( %d,%d,%d,%d )" % (self.head,self.head,self.head,self.head)

    def get_tiles(self):
        if self.type == Exposed.CHOW :
            return (self.head,self.head+1,self.head+2)
        elif self.type == Exposed.PUNG :
            return (self.head,self.head,self.head)
        elif self.type == Exposed.MINKONG :
            return (self.head,self.head,self.head,self.head)
        elif self.type == Exposed.APKONG :
            return (self.head,self.head,self.head,self.head)
        elif self.type == Exposed.CONCKONG :
            return (self.head,self.head,self.head,self.head)

    def toDict(self):
        return {"type":self.__class__.__TYPENAMES__[self.type] , "tiles":self.get_tiles() }


    def mentu_id(self):
        return self.head

    def is_kong(self):
        return self.type >= Exposed.MINKONG
    def is_pong(self):
        return self.type >= Exposed.PUNG
    def is_concealed(self):
        return self.type == Exposed.CONCKONG

    def toJSON(self):
        return self.__dict__
