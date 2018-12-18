# -*- coding : utf8 -*-

import numpy as np
from matplotlib import pyplot as plt
from .judge.util import *
from .judge.shanten import shanten

from .structs import *

import asyncio,promise
from promise import Promise
import time

import traceback
import threading




class AITsumogiri:
    def __init__(self):
        pass

    def select_discard(self,pl,game):
        return len(pl.hand)-1

    def get_name(self):
        return "ツモ切りAIちゃん"

    async def turn_command_async(self,pl,game,commands):
        return TurnCommand(TurnCommand.DISCARD,-1)

    async def command_async(self,pl,game,commands):
        return Claim(0)

    async def confirm(self,message):
        pass

    async def message(self,message):
        pass

    async def send(self,obj):
        pass

class AIShanten:
    def __init__(self):
        pass

    def get_name(self):
        return "よわいAIちゃん"

    def select_discard(self,pl,game):
        ary = list_to_array(pl.hand)
        e = np.eye( 64 , dtype = np.int32 )
        q = np.tile(ary, (len(pl.hand),1) ) - e[pl.hand]
        p = np.apply_along_axis( shanten , 1 , q )
        return np.argmin(p)

    async def turn_command_async(self,pl,game,commands):
        return TurnCommand(TurnCommand.DISCARD,-1)

    async def command_async(self,pl,game,commands):
        return Claim(0)


    async def confirm(self,message):
        pass

    async def message(self,message):
        pass

    async def send(self,obj):
        pass

class RemotePlayer:

    def __init__(self,connection):
        self.conn = connection

    def get_name(self):
        
        return str( self.conn.get_user() )

    def send(self,obj):
        if not hasattr(self,"conn") :
            raise Exception("No connection")

    async def turn_command_async(self,pl,game,commands):
        obj = { "type":"your_turn" , "hand_tiles":pl.hand , "draw":pl.drew , "turn_commands_available" : commands }
        if pl.agari_infos is not None :
            obj["agari_info"] = pl.agari_infos

        try:
            res = await self.conn.send_and_receive_reply( obj ,timeout=game.timeout)
            res = TurnCommand.fromDict(res)
            return res
        except Exception as e :
            traceback.format_exc()
            return TurnCommand(TurnCommand.DISCARD,-1)

    async def command_async(self,pl,game,commands):
        obj = { "type": "claim_command" , "hand_tiles":pl.hand , "target":{"player":game.turn, "apkong":game.apkong , "tile" : game.target_tile } , "commands_available" : commands }
        if pl.agari_infos is not None :
            obj["agari_info"] = pl.agari_infos
        try:
            res = await self.conn.send_and_receive_reply( obj ,timeout=game.timeout)
            res = Claim.fromDict(res)
            return res
        except Exception as e :
            traceback.format_exc()
            return Claim(0)

    async def confirm(self,message):
        obj = { "type": "confirm" , "message":message }
        try:
            await self.conn.send_and_receive_reply( obj ,timeout=3000)
        except Exception as e :
            traceback.format_exc()
            return

    async def message(self,message):
        obj = { "type": "message" , "message":message }
        await self.conn.send(obj)

    async def send(self,obj):
        await self.conn.send(obj)
