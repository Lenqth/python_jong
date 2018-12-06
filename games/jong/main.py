

from .game import *
from .player import *
from .agent import *

import asyncio
from promise import Promise

from .models import GameJongResult

async def main(conns,room):
    game = Game(room.config)
    result = GameJongResult()
    for i in range(4):
        game.players[i].agent = AITsumogiri()
    users = [None] * 4
    game.players[0].agent = RemotePlayer( conns[0] )
    users[0] = conns[0].get_user()
    if len(conns) >= 2:
        game.players[2].agent = RemotePlayer( conns[1] )
        users[2] = conns[1].get_user()
    if len(conns) >= 3:
        game.players[1].agent = RemotePlayer( conns[2] )
        users[1] = conns[2].get_user()
    if len(conns) >= 4:
        game.players[3].agent = RemotePlayer( conns[3] )
        users[3] = conns[3].get_user()
    tasks = [ c.receive_any(timeout=60) for c in conns ]
    tasks2 = [ c.send( { "start" : "1" } ) for c in conns ]
    await Promise.all(tasks2)
    await Promise.all(tasks)
    try:
        result.player1 = users[0] if users[0] and users[0].is_authenticated else None
        result.player2 = users[1] if users[1] and users[1].is_authenticated else None
        result.player3 = users[2] if users[2] and users[2].is_authenticated else None
        result.player4 = users[3] if users[3] and users[3].is_authenticated else None
        result.save()
        res = await game.run()
        result.score1 = res[0]
        result.score2 = res[1]
        result.score3 = res[2]
        result.score4 = res[3]
        result.save()
        await game.send_final_result()
        
    except Exception as e :
        traceback.print_exc()
        raise e


def config():
    obj = {}
    obj["room_size"] = { "display_name":"人数" , "default":2 , "value":[1,2,4]  }
    obj["iteration"] = { "display_name":"局数" , "default":4 , "value":[1,2,4,8,16]  }
    obj["timeout"] = { "display_name":"制限時間" , "default":30 , "value":[15,30,60,300]  }
    obj["minimum_value"] = { "display_name":"最低点数" , "default":8 , "value":[-9,-8,-3,-2,0,4,6,8,12,16]  }
    return obj
