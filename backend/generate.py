from skifree.server import *
import json

game = GameRoom(GameParameters())
player = game.create_player(None)
payload = game.get_player_payload(player)

with open('game.json', 'w') as f:
    f.write(json.dumps(payload, indent=2))

