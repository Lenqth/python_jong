# -*- coding: utf-8 -*-

try:
    from .util import *
    from .config import *
except:
    from util import *
    from config import *

import numpy as np
import functools
import itertools


def contain_knit(ary):
    a,b,c = map(to_bits,[ary[1:10],ary[17:26],ary[33:42]])
    print(a,b,c)
    q = False
    full = (1 << 9) - 1
    m1 = 1 | 1 << 3 | 1 << 6
    m2 = m1<<1
    m3 = m1<<2
    q |= ( full == ( a & m1 ) | ( b & m2 ) | ( c & m3 ) )
    q |= ( full == ( a & m1 ) | ( c & m2 ) | ( b & m3 ) )
    q |= ( full == ( b & m1 ) | ( a & m2 ) | ( c & m3 ) )
    q |= ( full == ( b & m1 ) | ( c & m2 ) | ( a & m3 ) )
    q |= ( full == ( c & m1 ) | ( a & m2 ) | ( b & m3 ) )
    q |= ( full == ( c & m1 ) | ( b & m2 ) | ( a & m3 ) )
    return q


def _colorwise_mentsu(ary,is_number=True):
    res = []
    def _colorwise_mentsu_internal(k,dat):
        if k>9:
            res.append( dat.copy() )
            return
        f = True
        left = dat[0]
        mp = dat[1]
        mc = dat[2]
        if left[k] >= 3 :
            mp[k] += 1
            left[k] -= 3
            _colorwise_mentsu_internal(k,dat)
            mp[k] -= 1
            left[k] += 3

        if is_number and (left[k:k+3] > 0).all():
            mc[k] += 1
            left[k:k+3] -= 1
            _colorwise_mentsu_internal(k,dat)
            mc[k] -= 1
            left[k:k+3] += 1

        _colorwise_mentsu_internal(k+1,dat)

    defdat = np.zeros( (3,16) ,dtype=np.int16)
    defdat[0,:] = ary
    _colorwise_mentsu_internal(0,defdat)
    max_m = max(map(lambda x:np.sum(x[1:3,:]),res))
    return list(filter(lambda x:np.sum(x[1:3,:])==max_m,res))

def expect_mentu(ary,expect=4):
    ml=_colorwise_mentsu(ary[0:16])
    pl=_colorwise_mentsu(ary[16:32])
    sl=_colorwise_mentsu(ary[32:48])
    cl=_colorwise_mentsu(ary[48:64],is_number=False)
    res = []
    buff = np.zeros( (2,4,16) , dtype = np.int16 )
    for (m,p,s,c) in itertools.product(ml,pl,sl,cl):
        cnt = np.sum(m[1:3,:])+np.sum(p[1:3,:])+np.sum(s[1:3,:])+np.sum(c[1:3,:])
        if cnt < expect :
            continue
        if  ( m[0] == 2 ).any() :
            buff[:,0,:] = m[1:3];buff[:,1,:] = p[1:3];buff[:,2,:] = s[1:3];buff[:,3,:] = c[1:3]
            atama = np.where( m[0] == 2 )[0][0]
            res.append( ( buff.copy() , atama ) )
        elif ( p[0] == 2 ).any() :
            buff[:,0,:] = m[1:3];buff[:,1,:] = p[1:3];buff[:,2,:] = s[1:3];buff[:,3,:] = c[1:3]
            atama = np.where( p[0] == 2 )[0][0] + 16
            res.append( ( buff.copy() , atama ) )
        elif ( s[0] == 2 ).any() :
            buff[:,0,:] = m[1:3];buff[:,1,:] = p[1:3];buff[:,2,:] = s[1:3];buff[:,3,:] = c[1:3]
            atama = np.where( s[0] == 2 )[0][0] + 32
            res.append( ( buff.copy() , atama ) )
        elif ( c[0] == 2 ).any() :
            buff[:,0,:] = m[1:3];buff[:,1,:] = p[1:3];buff[:,2,:] = s[1:3];buff[:,3,:] = c[1:3]
            atama = np.where( c[0] == 2 )[0][0] + 48
            res.append( ( buff.copy() , atama ) )
    if len(res) == 0:
        return None
    return res

def agari_kokushi(ary,exposed_mentu=0):
    if exposed_mentu > 0:
        return None
    cnt = ary[YAOCHU]
    fq = np.bincount(cnt,minlength=5)
    return True if (fq[1] == 12 and fq[2] == 1) else None

def agari_7pairs(ary,exposed_mentu=0):
    if exposed_mentu > 0:
        return None
    fq = np.bincount(ary,minlength=5)
    if fq[2] == 7 :
        return True
    if ALLOW_FOUR_IN_7PAIRS and ( fq[2] + fq[4] * 2 ) == 7 :
        return True
    return None

def agari_knitted_normal(ary,exposed_mentu=0):
    if exposed_mentu > 1:
        return None
    for i in range(6):
        left = ary - KNITS[i]
        if (left >= 0).all() :
            r = expect_mentu(left,expect=1-exposed_mentu)
            if r is not None :
                return r
    return None

def agari_knitted(ary,exposed_mentu=0):
    if exposed_mentu > 0:
        return None
    for i in range(6):
        if (ary <= KNITMASK[i] ).all() :
            return True
    return None

def agari_normal(ary,exposed_mentu=0):
    if exposed_mentu > 4:
        return None
    r = expect_mentu(ary,expect=4-exposed_mentu)
    if r is not None :
        return r
    return None

def is_agari(ary,exposed_mentu=0):
    assert( 0 <= exposed_mentu <= 4 )
    res = []
    if exposed_mentu == 0 :
        r = agari_kokushi(ary,exposed_mentu)
        if r is not None:
            return [{"type":"kokushi","data":r}]
        r = agari_knitted(ary,exposed_mentu)
        if r is not None:
            return [{"type":"knitted","data":r}]
        r = agari_7pairs(ary,exposed_mentu)
        if r is not None:
            res.append( {"type":"7pairs","data":r} )
    r = agari_knitted_normal(ary,exposed_mentu)
    if r is not None:
        res.extend( map( lambda x:{"type":"knitted_normal","data":x[0],"atama":x[1]} , r ) )
    r = agari_normal(ary,exposed_mentu)
    if r is not None:
        res.extend( map( lambda x:{"type":"normal","data":x[0],"atama":x[1]} , r ) )
    if len(res) == 0:
        return None
    return res

class Agari:
    def __init__(self):
        pass

    def is_agari(ary,expose=[]):
        pass

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



if __name__ == "__main__":
#    print( contain_knit(knithand) )
    from pprint import pprint
    #print( _colorwise_mentsu( [0, 0, 0, 0, 0, 2, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0] ) )
    #print( expect_mentu(string_to_array("55678s455667p"),expect=3) )
    #pprint( is_agari( string_to_array("123123m345789s55p") )[0]["data"].shape )
    #unittest.main()
