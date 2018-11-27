# -*- coding : utf8 -*-

import numpy as np
import sys,os

from functools import total_ordering

import asyncio

# from ai import *
from .player import *

from .judge.agari import is_agari
from .judge.shanten import shanten
from .judge.util import *

async def pure_async(x):
    return x

def safe_get(dic,key,default=None):
    if key in dic  :
        return dic[key]
    else:
        return default

class Game:
    async def send_deck_left(self):
        obj = {
            "type" : "deck_left",
            "deck_left" : self.lefttile()
            }
        t = []
        for i in range(4):
            pl = self.players[i]
            t.append( pl.agent.send( obj ) )
        await Promise.all(t)

    async def send_all_state(self,pid):
        pls = [ self.players[i].get_data(self,pid) for i in range(4) ]
        obj = {
            "type" : "reset",
            "deck_left" : self.lefttile(),
            "player_id" : pid ,
            "seat_wind" : self.get_seat_wind(pid) ,
            "prev_wind" : self.prevalent_wind ,
            "players" : pls
        }
        await self.players[pid].agent.send(obj)


    async def send_discard(self,pid,tile):
        t = []
        for i in range(4):
            pl = self.players[i]
            t.append( pl.agent.send({"type":"discard","tile":tile,"pid":pid}) )
        await Promise.all(t)

    async def send_apkong(self,pid,tile):
        t = []
        for i in range(4):
            pl = self.players[i]
            t.append( await pl.agent.send({"type":"apkong","tile":tile,"pid":pid}) )
        await Promise.all(t)

    async def send_expose(self,pid,obj):
        t = []
        for i in range(4):
            pl = self.players[i]
            t.append( await pl.agent.send({"type":"expose","obj":obj.toDict(),"pid":pid}) )
        await Promise.all(t)

    async def send_agari(self,pid,tsumo,kousei,yaku):
        print("send_agari")
        t = []
        for i in range(4):
            pl = self.players[i]
            t.append( await pl.agent.send( {"type":"agari","tsumo":tsumo,"kousei":kousei,"yaku":yaku,"pid":pid}) )
            t.append( await pl.agent.send( {"type":"open_hand","hand":[{"hand":self.players[i].hand,"drew":self.players[i].drew} for i in range(4)]}) )
        await Promise.all(t)

    async def send_ryukyoku(self):
        t = []
        for i in range(4):
            pl = self.players[i]
            t.append( await pl.agent.send( {"type":"gameover"}) )
            t.append( await pl.agent.send( {"type":"open_hand","hand":[{"hand":self.players[i].hand,"drew":self.players[i].drew} for i in range(4)]}) )
        await Promise.all(t)

    def __init__(self,config):
        self.config = config
        self.total_score = np.zeros( 4 , np.int16 )
        self.timeout = safe_get(config,"timeout",30)
        self.is_ready = False
        self.players = [ Player(self,i) for i in range(4)]
        for i,p in enumerate( self.players ):
            p.agent = AITsumogiri()
        self.is_done = False
        self._prevalent_wind = 0
        self._seat_wind_offset = 0

    def get_seat_wind(self,pid):
        return ( self._seat_wind_offset + pid ) % 4

    @property
    def prevalent_wind(self):
        return self._prevalent_wind

    def init(self):
        self.turn = 0
        deck = np.array( [1,2,3,4,5,6,7,8,9,
                17,18,19,20,21,22,23,24,25,
                33,34,35,36,37,38,39,40,41,
                49,50,51,52,53,54,55] * 4 ) # + [56] * 8 )
        np.random.shuffle(deck)
        self.pile = deck
        self.pilepos = 0
        for p in self.players:
            p.reset()
            for i in range(13):
                p.hand.append(self.draw())
        #self.players[0].hand=[1,1,1,2,2,2,3,3,3,4,4,4,5]
        self.is_ready = True
        self.konged_tile = False

    def draw(self):
        # print("d:%d",len(self.pile)-self.pilepos)
        if self.pilepos >= len(self.pile):
            return None
        res = self.pile[self.pilepos]
        self.pilepos+=1
        self.konged_tile = False
        return res

    def lefttile(self):
        return len(self.pile) - self.pilepos

#    def run(self):
#        print("run start")
#        res = self.go()
#        self.reward = res
#        print( "END: reward = ( {0:>3} , {1:>3} , {2:>3} , {3:>3} )".format(*res) , flush=True )
#        print("run end")
#
#    def run_forever(self):
#        while True:
#            res = self.go()
#            self.reward = res
#            self.shanten_end = [ self.players[i].shanten() for i in range(4) ]
#            print( "{0:>3} , {1:>3} , {2:>3} , {3:>3} , {4:>3} , {5:>3} , {6:>3} , {7:>3}".format(*res , *self.shanten_end  ) , flush=True )

    async def run(self):
        self.total_score = np.zeros( 4 , np.int16 )
        for i in range(self.config["iteration"]):
            self._prevalent_wind = i // 4
            self._seat_wind_offset = i % 4
            res = await self.one_game()
            self.total_score += res
            confirm_tasks = [ p.agent.confirm("next") for p in self.players  ]
            Promise.all(confirm_tasks)
        return self.total_score

    async def one_game(self):
        self.is_done = False
        self.init()
        for p in self.players:
            p.hand.sort()
        self.skip_draw = False
        await Promise.all( [self.send_all_state(i) for i in range(4)] )
        while True:
            if self.skip_draw == False and self.players[self.turn].drew == None :
                tm = self.draw()
                await self.send_deck_left()
                if tm == None:
                    self.is_done = True
                    self.is_ready = False
                    await self.send_ryukyoku()
                    return (0,0,0,0) #流局
                self.players[self.turn].drew = tm
            self.skip_draw = False

            turn_player = self.players[self.turn]
            print("(player {0} , {1} tiles left)".format(self.turn,len(self.pile)-self.pilepos) , flush=True )

            turn_player.hand.sort()
            turn_command = await turn_player.turn(self) # 打牌 or 加槓/暗槓 or ツモ
            self.apkong = False
            if turn_command.type == TurnCommand.DISCARD :
                tsumogiri = turn_command.pos == -1
                if turn_player.drew is None and tsumogiri :
                    tsumogiri = False
                    turn_command.pos = len(turn_player.hand)-1
                tile = turn_player.pop_from_hand( turn_command.pos )
                obj = { "id":tile , "tsumogiri":tsumogiri , "yoko":False , "claimed":False }
                turn_player.trash.append( obj )
                await self.send_discard(self.turn, { "id":tile , "tsumogiri":tsumogiri , "yoko":False , "claimed":False } )
            elif turn_command.type == TurnCommand.APKONG :
                tile = turn_player.pop_from_hand( turn_command.pos )
                self.apkong = True
                await self.send_apkong(self.turn,tile)
            elif turn_command.type == TurnCommand.CONCKONG :
                ts = turn_player.pop_from_hand( turn_command.pos )
                assert( ts[0] == ts[1] and ts[1] == ts[2] and ts[2] == ts[3] )
                ex = Exposed(Exposed.CONCKONG,ts[0])
                turn_player.exposed.append(ex)
                if turn_player.drew is not None :
                    turn_player.hand.append(turn_player.drew)
                    turn_player.drew = None
                    turn_player.hand.sort()
                await self.send_expose(self.turn,ex)
                continue
            elif turn_command.type == TurnCommand.TSUMO :
                score_li = [-8,-8,-8,-8]
                score_li[:] -= turn_player.agari_infos[0]
                score_li[command_player_id] = 24 + turn_player.agari_infos[0] * 3
                self.is_done = True
                self.is_ready = False
                await self.send_agari(self.turn,True,turn_player.agari_infos,turn_player.agari_infos)
                return tuple(score_li)
            # print(tile)
            self.target_tile = tile
            print("DEBUG:BEFORE SUBTURN")
            subturn_tasks = [ None for i in range(4) ]
            for i in range(1,4): # 鳴き
                pi = ( self.turn + i ) % 4
                subturn_tasks[pi] = ( self.players[pi].subturn_async(self,tile,self.apkong) )
            subturn_tasks[self.turn] = pure_async( Claim(0) )
            command = await Promise.all(subturn_tasks)
            command_player_id = np.argmax(command)

            if command[command_player_id].type > 0 : # 鳴き/ロンがあった場合
                if command[command_player_id].type == Claim.RON :
                    self.players[command_player_id].drew = tile
                    agari_player = self.players[command_player_id]
                    score_li = [-8,-8,-8,-8]
                    score_li[self.turn] -= agari_player.agari_infos[0]
                    score_li[command_player_id] = 24 + agari_player.agari_infos[0]
                    self.is_done = True
                    self.is_ready = False
                    await self.send_agari(command_player_id,False,agari_player.agari_infos,agari_player.agari_infos)
                    return tuple(score_li)
                elif command[command_player_id].type == Claim.MINKONG :
                    a,b,c = filter( lambda x:x>=0 , command[command_player_id].pos  )
                    ct = self.players[command_player_id].hand.pop(c)
                    bt = self.players[command_player_id].hand.pop(b)
                    at = self.players[command_player_id].hand.pop(a)
                    ex = Exposed(Exposed.MINKONG,tile)
                    self.players[command_player_id].exposed.append(ex)
                    self.turn = command_player_id
                    self.konged_tile = True
                    turn_player.trash[-1]["claimed"] = True
                    await self.send_expose(command_player_id,ex)
                elif command[command_player_id].type == Claim.PUNG :
                    a,b = filter( lambda x:x>=0 , command[command_player_id].pos  )
                    bt = self.players[command_player_id].hand.pop(b)
                    at = self.players[command_player_id].hand.pop(a)
                    ex = Exposed(Exposed.PUNG,tile)
                    self.players[command_player_id].exposed.append(ex)
                    self.turn = command_player_id
                    self.skip_draw = True
                    turn_player.trash[-1]["claimed"] = True
                    await self.send_expose(command_player_id,ex)
                elif command[command_player_id].type == Claim.CHOW :
                    a,b = filter( lambda x:x>=0 , command[command_player_id].pos  )
                    bt = self.players[command_player_id].hand.pop(b)
                    at = self.players[command_player_id].hand.pop(a)
                    hd = min( at, bt , tile  )
                    ex = Exposed(Exposed.CHOW,hd)
                    self.players[command_player_id].exposed.append(ex)
                    self.turn = command_player_id
                    self.skip_draw = True
                    turn_player.trash[-1]["claimed"] = True
                    await self.send_expose(command_player_id,ex)

            if self.apkong :
                for ex in turn_player.exposed:
                    if ex.type == Exposed.PUNG :
                        if tile == ex.head :
                            ex.type = Exposed.APKONG
                            break

            if turn_player.drew is not None :
                turn_player.hand.append(turn_player.drew)
                turn_player.drew = None
                turn_player.hand.sort()
            turn_player.agari_infos = None

            if command[command_player_id].type <= 0 and ( not self.apkong ) :
                self.turn = ( self.turn + 1 ) % 4
