# -*- coding : utf8 -*-

import numpy as np
import sys,os

from functools import total_ordering

from .agent import *
from .structs import *

from .judge.agari import is_agari
from .judge.shanten import shanten
from .judge.scoring import ChineseScore
from .judge.util import *

import asyncio

def to_mentu(exposed):
    res = []
    for x in exposed:
        res.append(Mentu(x.type,x.head))
    return res


async def _sleep(n):
    await asyncio.sleep(n)

def to_back(ary):
    return [0]*len(ary)

class Player:
    def __init__(self,game,id):
        self.game = game
        self.id = id
        self.reset()

    def chk_agari(self,game,tile,tsumo):
        discarded_tiles = np.hstack( [ filter(lambda x:not x.claimed ,p.trash) for p in game.players ] )
        exposed_tiles = np.ravel( [ [ Mentu(x.type,x.head).get_tiles() for x in p.exposed ] for p in game.players ] , "C" )
        env = {
                        "prevalent_wind": game.prevalent_wind ,
                        "seat_wind": game.get_seat_wind(self.id),
                        "tsumo":tsumo ,
                        "deck_left":game.lefttile(),
                        "discarded_tiles": discarded_tiles ,
                        "exposed_tiles": exposed_tiles ,
                        "robbed_tile":False,
                        "konged_tile":False,
                     }
        res = ChineseScore.judge( self.hand+[tile] ,to_mentu(self.exposed),env=env,agari_tile=tile)
        self.agari_infos = res
        return (res is not None)

    def chk_claim(self,game,tile,apkong):
        res = []
        if self.chk_agari( game , tile , tsumo = False ): #ロン
            res.append( Claim(Claim.RON) )
        if apkong:
            return res
        fq = np.bincount(self.hand,minlength=64)
        a = np.array(self.hand)
        # chow
        if (game.turn+1)%4 == self.id and tile < 48: # number tiles
            if fq[tile-1] > 0 and fq[tile+1] > 0 :
                res.append( Claim( Claim.CHOW , [ np.where(a==tile-1)[0][0] , np.where(a==tile+1)[0][0] , -2 ] ) )
            if fq[tile+1] > 0 and fq[tile+2] > 0 :
                res.append( Claim( Claim.CHOW , [ np.where(a==tile+1)[0][0] , np.where(a==tile+2)[0][0] , -2 ] ) )
            if fq[tile-2] > 0 and fq[tile-1] > 0 :
                res.append( Claim( Claim.CHOW , [ np.where(a==tile-2)[0][0] , np.where(a==tile-1)[0][0] , -2 ] ) )
        # pung
        if fq[tile] >= 2 :
            res.append( Claim( Claim.PUNG , list( np.where(a==tile)[0][0:2] ) + [-2] ) )
        # kong
        if fq[tile] >= 3 :
            res.append( Claim( Claim.MINKONG , list( np.where(a==tile)[0][0:3] ) + [-2] ) )
        return res

    def chk_turn_claim(self,game):
        # apkong
        res = []
        for ex in self.exposed:
            if ex.type == Exposed.PUNG :
                for (p,t) in enumerate(self.hand) :
                    if t == ex.head :
                        res.append( TurnCommand(TurnCommand.APKONG,[p] , ex ) )
                if self.drew == ex.head :
                    res.append( TurnCommand(TurnCommand.APKONG,[-1] , ex ) )

        #conckong
        fq = np.bincount(self.hand,minlength=64)
        a = np.array(self.hand)
        for (t,q) in enumerate(fq) :
            if q >= 4 :
                arr = np.array(self.hand)
                res.append( TurnCommand(TurnCommand.CONCKONG, list(np.where(a == t)[0][0:4]) ) )
            elif q >= 3 and t == self.drew :
                arr = np.array(self.hand)
                res.append( TurnCommand(TurnCommand.CONCKONG, list(np.where(a == t)[0][0:3]) + [-1] ) )

        #tsumo
        if self.drew != None and self.chk_agari( game , self.drew , tsumo = True ):
            res.append( TurnCommand(TurnCommand.TSUMO) )
        return res

    def reset(self):
        self.hand = []
        self.trash = []
        self.exposed = []
        self.drew = None
        self.flower = 0

    def get_data(self,game,viewfrom):
        if viewfrom == self.id :
            return {
                "hand" : self.hand,
                "drew" : self.drew,
                "trash" : self.trash ,
                "exposed" : map(lambda x:x.toDict(),self.exposed) ,
                "flower" : self.flower,
                "score" : game.total_score[self.id]
            }
        else:
            return {
                "hand" : to_back(self.hand),
                "trash" : self.trash ,
                "exposed" : map(lambda x:x.toDict(),self.exposed) ,
                "flower" : self.flower,
                "score" : game.total_score[self.id]
            }

    async def turn(self,game):
        comm = self.chk_turn_claim(game)
        async def _subrt():
            return await self.agent.turn_command_async(self,game,comm)
        res = (await Promise.all( [_subrt(),_sleep(0.25)] ) )[0]
        return res

    async def subturn_async(self,game,tile,apkong): # opponent's turn Claim
        comm = self.chk_claim(game,tile,apkong)
        if len(comm) > 0:
            res = await self.agent.command_async(self,game,comm)
            return res
        else:
            return Claim(0)

    def pop_from_hand(self,position):
        import collections
        single = False
        if isinstance(position,collections.Iterable):
            position_list = sorted(list(position),reverse=True)
        else:
            single = True
            position_list = [position]
        res = []
        for x in position_list:
            if x == -1 :
                assert(self.drew is not None)
                res.append( self.drew )
                self.drew = None
            elif x >= 0:
                res.append( self.hand.pop(x) )
        if single :
            return res[0]
        else:
            return res

    def is_tsumo(self):
        return self.game.turn == self.id

    def hand_freq_array(self):
        return list_to_array(self.hand)

    def get_array(self,show_hand=False):
        res = np.zeros( (44,64) ,dtype=np.int16)
        e = np.eye( 64 )
        e[0] = 0
        trp = np.int16( np.pad( self.trash , [0,40-len(self.trash)] , "constant" ,constant_values = 0) )
        res[4:] = e[ trp ]
        if show_hand:
            res[0] = list_to_array(self.hand)
        return res

    def observe(self):
        res = np.zeros( (4,44,64) )
        for i in range(4):
            res[i] = self.game.players[ (i+self.id) % 4].get_array(show_hand=(i==0))
        return res

    def is_done(self):
        return self.game.is_done

    def get_reward(self):
        return self.game.reward[self.id]

    def shanten(self):
        return shanten(list_to_array(self.hand))
