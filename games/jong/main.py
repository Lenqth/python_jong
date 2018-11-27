

from .game import *
from .player import *
from .agent import *

import asyncio
from promise import Promise

async def main(conns,room):
    game = Game(room.config)
    for i in range(4):
        game.players[i].agent = AITsumogiri()
    game.players[0].agent = RemotePlayer( conns[0] )
    if len(conns) >= 2:
        game.players[2].agent = RemotePlayer( conns[1] )
    if len(conns) >= 3:
        game.players[1].agent = RemotePlayer( conns[2] )
    if len(conns) >= 4:
        game.players[3].agent = RemotePlayer( conns[3] )
    tasks = [ c.receive_any(timeout=60) for c in conns ]
    tasks2 = [ c.send( { "start" : "1" } ) for c in conns ]
    await Promise.all(tasks2)
    await Promise.all(tasks)

    try:
        await game.run()
    except Exception as e :
        traceback.print_exc()
        raise e


def config():
    obj = {}
    obj["room_size"] = { "display_name":"人数" , "default":2 , "value":[1,2,4]  }
    obj["iteration"] = { "display_name":"局数" , "default":4 , "value":[1,2,4,8,16]  }
    obj["timeout"] = { "display_name":"制限時間" , "default":30 , "value":[15,30,60,300]  }

    return obj
