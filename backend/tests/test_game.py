from skifree.server import *

def test_create_game():
    game = GameRoom(GameParameters())
    player = game.create_player(None)
    game.get_player_perspective(player)
