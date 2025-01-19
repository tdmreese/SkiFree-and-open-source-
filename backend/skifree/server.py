import asyncio
import websockets
import logging 
import json 
import numpy as np 
import matplotlib.pyplot as plt

from skifree.models import *
from websockets.asyncio.server import serve
from typing import Literal, Optional
from pathlib import Path
from pydantic import BaseModel, Field

# CONSTANTS
# ---------
HOSTNAME = 'localhost'
PORT = 8765
LOGFILE_PATH = Path(__file__).parent / 'server.log' # The same folder as this module

# LOGGING
# -------
logger = logging.getLogger('skifree')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

file_handler = logging.FileHandler(LOGFILE_PATH)
file_handler.setLevel(logging.WARNING)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# MODELS
# ------


# GAME
# ----
class ColorCycler:
    """Basic color cycler
    
    Usage: 
    ```
    cycler = ColorCycler()
    for i in range(10):
        print(cycler.get_color())
    ```
    """
    _color_cycle = [
        "#0000FF",  # blue
        "#008000",  # green
        "#FFFF00",  # yellow
        "#800080",  # purple
        "#FFA500",  # orange
    ]

    def __init__(self):
        self.index = 0

    def get_color(self):
        color = self._color_cycle[self.index]
        self.index = (self.index + 1) % len(self._color_cycle)
        return color


class StartPositionCycler:
    """Basic start position cycler
    
    Usage: 
    ```
    cycler = StartRecycler(map_width=100, map_height=100)
    for i in range(10):
        print(cycler.get_start())
    ```
    """
    def __init__(self, start_box_width: float, map_width: int, map_height: int):
        self.map_width = map_width
        self.map_height = map_height
        self.start_box_width = start_box_width
        self.index = 0

    def get_start_position(self):
        x = self.map_width // 2 
        y = 0
        self.index += 1
        return Position(x=x, y=y)

class GameRoom:
    def __init__(self, game_parameters: GameParameters):
        self.game_parameters = game_parameters
        
        self.player_count = 0 # This is not the same as the number of players in the game
        self.players = []

        self.game_objects = []
        self.object_positions = np.array([])

        # These cyclers will be used to assign colors and start positions to players who just join
        self.player_color_cycler = ColorCycler()
        self.player_start_cycler = StartPositionCycler(
            start_box_width=game_parameters.player_start_distance,
            map_width=game_parameters.width,
            map_height=game_parameters.height,
        )

    def generate_map(self):
        logger.info("Generating map")

        # Create the obstacles
        obstacles = []
        for _ in range(self.game_parameters.n_obstacles):
            obstacle_type = np.random.choice([Tree, Rock])
            x = np.random.uniform(low=0, high=self.game_parameters.width)
            y = np.random.uniform(
                low=self.game_parameters.object_start_offset, 
                high=self.game_parameters.height - self.game_parameters.finish_line_offset
            )
            obstacles.append(
                obstacle_type(position=Position(x=x, y=y), radius=1.0)
            )

        # Create the powerups
        powerups = []
        for _ in range(self.game_parameters.n_powerups):
            x = np.random.uniform(low=0, high=self.game_parameters.width)
            y = np.random.uniform(
                low=self.game_parameters.object_start_offset, 
                high=self.game_parameters.height - self.game_parameters.finish_line_offset
            )
            powerups.append(
                Jump(position=Position(x=x, y=y))
            )

        # Add the finish flags
        finish_flags = []
        for x in np.arange(0, self.game_parameters.width, 20):
            finish_flags.append(
                FinishFlag(position=Position(x=x, y=self.game_parameters.height - self.game_parameters.finish_line_offset))
            )
        
        self.game_objects = obstacles + powerups + finish_flags
        logger.info(f"Map generated with {len(self.game_objects)} objects")

    def render_game_plot(self):
        plt.figure(
            figsize=(self.game_parameters.width / 100, self.game_parameters.height / 100)
        )
        plt.xlim(0, self.game_parameters.width)
        plt.ylim(0, self.game_parameters.height)
        for game_object in self.game_objects:
            if isinstance(game_object, Tree):
                triangle = plt.Polygon([
                    (game_object.position.x, game_object.position.y + 6),
                    (game_object.position.x + 3, game_object.position.y - 3),
                    (game_object.position.x - 3, game_object.position.y - 3),
                ], closed=True, fill=True, edgecolor='green')
                plt.gca().add_patch(triangle)
            elif isinstance(game_object, Rock):
                circle = plt.Circle(
                    (game_object.position.x, game_object.position.y),
                    game_object.radius,
                    color='gray',
                )
                plt.gca().add_patch(circle)
            elif isinstance(game_object, Jump):
                square = plt.Rectangle(
                    (game_object.position.x - 3, game_object.position.y - 3),
                    6, 6,
                    color='blue',
                )
                plt.gca().add_patch(square)
            elif isinstance(game_object, FinishFlag):
                triangle = plt.Polygon([
                    (game_object.position.x, game_object.position.y + 6),
                    (game_object.position.x + 3, game_object.position.y - 3),
                    (game_object.position.x - 3, game_object.position.y - 3),
                ], closed=True, fill=True, edgecolor='red')
                plt.gca().add_patch(triangle)
            elif isinstance(game_object, StartFlag):
                pass
            elif isinstance(game_object, PlayerObject):
                pass
            else:
                pass

        plt.savefig('game_plot.png')
        plt.clf()
        plt.close()

        logger.info("Game plot saved to game_plot.png")

    def get_player_payload(self, player):
        # Remove this later
        player.camera.position.x = player.position.x
        player.camera.position.y = player.position.y

        # Get the object array
        object_positions = np.array([
            [obj.position.x, obj.position.y] for obj in self.game_objects
        ])

        xmin = player.camera.position.x - player.camera.view_width // 2 - player.camera.view_buffer
        xmax = player.camera.position.x + player.camera.view_width // 2 + player.camera.view_buffer
        ymin = player.camera.position.y - player.camera.view_height // 2 - player.camera.view_buffer
        ymax = player.camera.position.y + player.camera.view_height // 2 + player.camera.view_buffer

        # Get the objects in the player's view
        in_player_view = (
            (object_positions[:, 0] >= xmin) & (object_positions[:, 0] <= xmax) &
            (object_positions[:, 1] >= ymin) & (object_positions[:, 1] <= ymax)
        )

        _game_objects = np.array(self.game_objects)

        return {
            'game_objects': [o.model_dump(mode='json') for o in _game_objects[in_player_view].tolist()],
            'camera_params': player.camera.model_dump(mode='json'),
        }


    def send_game_update(self):
        for player in self.players:
            pass
            
    def game_loop(self):
        pass

    def create_player(self, connection: websockets.asyncio.server.ServerConnection):
        player = PlayerObject(
            connection=connection,
            id=self.player_count,
            color=self.player_color_cycler.get_color(),
            position=self.player_start_cycler.get_start_position(),
            speed=0,
            angle=0,
        )

        if len(self.players) == 0:
            self.generate_map()

        self.player_count += 1
        self.players.append(player)
        self.game_objects.append(player)
        return player

    def remove_player(self, player: PlayerObject):
        self.players.remove(player)
        self.game_objects.remove(player)
        

# WEBSOCK CONNECTIONS
# -------------------
game = GameRoom(GameParameters())
logger.info("Game room created")

async def echo(websocket):
    logger.info(f"New connection from {websocket.remote_address}")
    await websocket.send("Hello, Client!")

    # Create a player object (this will automatically add the player to the game)
    player = game.create_player(websocket)
    logger.debug(f"Player {player.id} created: {player.model_dump(mode='json')}")
    try:
        async for message in websocket:
            # Handle messages from the client
            try: 
                json_message = json.loads(message)
                if 'type' in json_message:
                    if json_message['type'] == 'action':
                        logger.info(f"Received action: {json_message['action']}")
                        ret = player.handle_input(json_message['action'])
                        if ret:
                            await websocket.send("Action received: move")
                        else:
                            await websocket.send("Invalid action")

                    else:
                        logger.warning(f"Invalid message type: {json_message}")

            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON message: {message}")
                continue
            

    except websockets.ConnectionClosed as e:
        logger.info(f"Connection closed: {e}")
    finally:
        logger.info(f"Connection with {websocket.remote_address} closed")
        game.remove_player(player)
        logger.debug(f"Player {player.id} removed: {player.model_dump(mode='json')}")

async def main():
    async with serve(echo, HOSTNAME, PORT) as server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())
