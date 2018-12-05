
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


if ALLOW_KNITTED :
    def shanten_knitted(ary):
        return min( [ 13 - len(ary[KNITNUMS[i]].nonzero()[0] ) for i in range(6)] )
else:
    def shanten_knitted(ary):
        return 99



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

_colorwise_parts_memory = np.full( (5**9*2) , None , dtype=np.object )
def _colorwise_parts_cached(ary,is_number=True):
    idx = __to_number(ary)
    isn = 1 if is_number else 0
    if idx == None:
        return _colorwise_parts(ary,is_number=is_number)
    r = _colorwise_parts_memory[ (idx << 1) | isn ]
    if r is None :
        #print("CACHE MISS : {0} {1} ({2})".format(ary,isn,idx))
        v = _colorwise_parts(ary,is_number=is_number)
        _colorwise_parts_memory[(idx << 1) | isn] = v
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
    res = np.zeros( (6,2) ,dtype=np.int16)
    def _colorwise_parts_internal(k,ty,left,p3,p2,pair):
        nonlocal res
        if k>9 or p3 + p2 >= 5 :
            res[p3+p2][pair] = max( res[p3+p2][pair] , p3*2 + p2 )
            res[p3+p2][0] = max( res[p3+p2][0] , p3*2 + p2 )
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



TMP_FOR_SHANTENEXP = np.full( (4,5,2), -1 , dtype=np.int16)
def shanten_exp(ary,expect=4,atama=True):
    res = [
        _colorwise_parts_cached(ary[0:16]),
        _colorwise_parts_cached(ary[16:32]),
        _colorwise_parts_cached(ary[32:48]),
        _colorwise_parts_cached(ary[48:64],is_number=False)
    ]
    TMP_FOR_SHANTENEXP.fill(-1)
    def shanten_exp_int(k,m,p):
        if k<0 or (m|p)==0 :
            return 0
        if TMP_FOR_SHANTENEXP[k,m,p] != -1:
            return TMP_FOR_SHANTENEXP[k,m,p]
        m1 = range(m+1)
        r = max( [shanten_exp_int(k-1,m-i,p)+res[k][i,0] for i in m1] )
        if p>0:
            r = max( r, max( [shanten_exp_int(k-1,m-i,0)+res[k][i+1,1] for i in m1 ] ) )
        TMP_FOR_SHANTENEXP[k,m,p] = r
        return r
    mv = shanten_exp_int(3,expect,1)
    return expect*2 - mv

if ALLOW_KNITTED_NORMAL :
    def shanten_knitted_normal(ary):
        v = np.zeros(6,dtype=np.int16)
        for i in range(6):
            p = ary - KNITS[i]
            left = np.maximum( p , 0 )
            a = shanten_exp(left,expect=1)
            b = np.sum( left - p )
            v[i] = a + b

        return np.min(v)
else:
    def shanten_knitted_normal(ary):
        return 99

def shanten_normal(ary):
    return shanten_exp(ary,expect=4)


def shanten(ary):
    return min( shanten_kokushi(ary) , shanten_7pairs(ary) , shanten_knitted(ary) , shanten_knitted_normal(ary) , shanten_normal(ary) )


#if __name__ == '__main__':
    #print( shanten_exp(to_array(sou="1239",ji="3"),expect=1) )
    #print( shanten_knitted_normal( to_array(man="12344567",pin="258",sou="36",ji="5") ) )
    #print( shanten_exp(to_array(sou="167",ji="33"),expect=1) )
    #print( shanten_normal( to_array(man="11123678999",pin="19",sou="",ji="") ) )
    #unittest.main()
    #all_cache_calculation()
    #q = 0
    #for i in range(10000):
    #    q += shanten(randomhand())
    #print( q / 10000.0 )
#    import cProfile
#    cProfile.run('[ shanten(randomhand()) for i in range(1000) ]')
