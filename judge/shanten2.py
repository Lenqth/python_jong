
# -*- coding: utf-8 -*-

try:
    from .util import *
    from .config import *
except:
    from util import *
    from config import *

import numpy as np
import functools,itertools


def shanten_kokushi(ary):
    cnt = ary[YAOCHU]
    fq = np.bincount(cnt,minlength=5)
    res = 13 - np.sum(fq[1:])
    if np.sum(fq[2:]) > 0 :
        res -= 1
    return res

def shanten_7pairs(ary):
    fq = np.bincount(ary,minlength=5)
    if ALLOW_FOUR_IN_7PAIRS :
        return 6 - (np.sum(fq[2:]) + np.sum(fq[4:]))
    else:
        res = 6 - np.sum(fq[2:])
        ts = np.sum(fq[1:])
        if ts < 7:
            res += 7 - ts
        return res


def shanten_knitted(ary):
    return np.min( [ 13 - len(ary[KNITNUMS[i]].nonzero()[0] ) for i in range(6)] )

FIVES = np.array( [ ( 5**(i-1) if 1 <= i <= 9 else 0 ) for i in range(16)] )

if ORTHODOX_MODE:
    def __to_number(ary):
        return np.dot( ary , FIVES )
else:
    def __to_number(ary):
        nz = ary.nonzero()[0]
        if np.max(ary) <= 4 and ( (1 <= nz) & (nz <= 9) ).all():
            return None
        return np.dot( ary , FIVES )

_colorwise_parts_memory = np.full( (5**9,2) , None , dtype=np.object )
def _colorwise_parts_cached(ary,is_number=True):
    idx = __to_number(ary)
    isn = 1 if is_number else 0
    if idx is None:
        return _colorwise_parts(ary,is_number=is_number)
    r = _colorwise_parts_memory[idx,isn]
    if r is None :
        #print("CACHE MISS : {0} {1} ({2})".format(ary,isn,idx))
        v = _colorwise_parts(ary,is_number=is_number)
        _colorwise_parts_memory[idx,isn] = v
        v.flags.writeable = False
        return v
    else:
        #print("CACHE HIT : {0} {1} ({2})".format(ary,isn,idx))
        return r

def all_cache_calculation():
    ary = np.zeros( 16 , dtype = np.int16)
    i = 0
    t = 0
    for q in itertools.product( *( [[0,1,2,3,4]]*9) ):
        i += 1
        if i > 100000:
            t += i
            print(t)
        if np.sum(q) > 14 :
            continue
        ary[1:10] = q
        _colorwise_parts_cached(ary,False)
        _colorwise_parts_cached(ary,True)

def _colorwise_parts(ary,is_number=True):
    res = np.zeros( (2,6) ,dtype=np.int16)
    def _colorwise_parts_internal(k,ty,left,p3,p2,pair):
        nonlocal res
        if k>9 or p3 + p2 >= 5 :
            res[pair][p3+p2] = max( res[pair][p3+p2] , p3*2 + p2 )
            return
        if left[k] > 0:
            if ty <= 0 and left[k] >= 2 :
                left[k] -= 2
                _colorwise_parts_internal(k,0,left,p3,p2 + 1,1)
                left[k] += 2
            if p3 + p2 >= 4 and pair == 0 :
                return
            if ty <= 1 and left[k] >= 3 :
                left[k] -= 3
                _colorwise_parts_internal(k,1,left,p3+1,p2,pair)
                left[k] += 3
            if is_number :
                if ty <= 2 and (left[k:k+3] > 0).all():
                    left[k:k+3] -= 1
                    _colorwise_parts_internal(k,2,left,p3+1,p2,pair)
                    left[k:k+3] += 1
                else:
                    if ty <= 3 and is_number and left[k+1] > 0:
                        left[ [k,k+1] ] -= 1
                        _colorwise_parts_internal(k,3,left,p3,p2+1,pair)
                        left[ [k,k+1] ] += 1
                    if ty <= 4 and is_number and left[k+2] > 0:
                        left[ [k,k+2] ] -= 1
                        _colorwise_parts_internal(k,4,left,p3,p2+1,pair)
                        left[ [k,k+2] ] += 1
        _colorwise_parts_internal(k+1,0,left,p3,p2,pair)
    defdat = np.copy(ary)
    _colorwise_parts_internal(0,0,defdat,0,0,0)
    return res

from scipy.ndimage.interpolation import shift as spshift
def maxplus_convolve(a,b):
    p = np.zeros( (6,6) , dtype=np.int16 )
    q = np.zeros( (6,6) , dtype=np.int16 )
    p[:] = a
    for i in range(6):
        q[i,:] = np.roll( b, i)
    q = np.flip(np.flip(q,axis=0),axis=1)
    r=p+q
    r[np.triu_indices(6, k = 1)] = 0
    return np.max( r , axis = 1)

def shanten_exp(ary,expect=4,atama=True):
    res = np.ndarray( (4,2,6) , dtype=np.int64 )
    res[0,:,:] = _colorwise_parts_cached(ary[0:16])
    res[1,:,:] = _colorwise_parts_cached(ary[16:32])
    res[2,:,:] = _colorwise_parts_cached(ary[32:48])
    res[3,:,:] = _colorwise_parts_cached(ary[48:64],is_number=False)
    def cv(a,b,c,d,n):
        return np.max( maxplus_convolve(maxplus_convolve(maxplus_convolve(a,b),c),d)[0:n] )
    mv = np.max([cv( res[0,0] , res[1,0] , res[2,0] , res[3,0] ,5) ,
                cv( res[0,1] , res[1,0] , res[2,0] , res[3,0] ,6) ,
                cv( res[0,0] , res[1,1] , res[2,0] , res[3,0] ,6) ,
                cv( res[0,0] , res[1,0] , res[2,1] , res[3,0] ,6) ,
                cv( res[0,0] , res[1,0] , res[2,0] , res[3,1] ,6) ])
    return expect*2 - mv

def shanten_knitted_normal(ary):
    v = np.zeros(6,dtype=np.int16)
    for i in range(6):
        p = ary - KNITS[i]
        left = np.maximum( p , 0 )
        a = shanten_exp(left,expect=1)
        b = np.sum( left - p )
        v[i] = a + b

    return np.min(v)

def shanten_normal(ary):
    return shanten_exp(ary,expect=4)


def shanten(ary):
    return min( shanten_kokushi(ary) , shanten_7pairs(ary) , shanten_knitted(ary) , shanten_knitted_normal(ary) , shanten_normal(ary) )



import unittest

class TestShanten(unittest.TestCase):

    def test_kokushi(self):
        self.assertEqual( 0 , shanten_kokushi( to_array(man="19",pin="19",sou="199",ji="123456") ) )

    def test_7pairs(self):
        self.assertEqual( 1 , shanten_7pairs( to_array(man="11",pin="225566",sou="34",ji="133") ) )

    def test_knitted(self):
        self.assertEqual( 1 , shanten_knitted( to_array(man="147",pin="25",sou="3",ji="12345567") ) )

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
import cProfile

if __name__ == '__main__':
    #print( shanten_exp(to_array(sou="1239",ji="3"),expect=1) )
    #print( shanten_knitted_normal( to_array(man="12344567",pin="258",sou="36",ji="5") ) )
    #print( shanten_exp(to_array(sou="167",ji="33"),expect=1) )
    #print( shanten_normal( to_array(man="11123678999",pin="19",sou="",ji="") ) )
    #unittest.main()
    #all_cache_calculation()
    #for i in range(10000):
    #    shanten(randomhand())

    cProfile.run('[ shanten(randomhand()) for i in range(1000) ]')
