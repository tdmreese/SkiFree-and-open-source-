from pydantic import BaseModel, Field, ConfigDict
from typing import Literal, Optional
from websockets.asyncio.server import ServerConnection

class Position(BaseModel):
    x: float
    y: float
    z: float = 0.0

class MapObject(BaseModel):
    type: str
    position: Position
    height: float = 0.0

class Obstacle(MapObject):
    radius: float

class Tree(Obstacle):
    type: Literal['tree'] = 'tree'
    radius: float = Field(default=1.0)

class Rock(Obstacle):
    type: Literal['rock'] = 'rock'
    radius: float = Field(default=1.0)

class Jump(MapObject):
    type: Literal['jump'] = 'jump'

class FinishFlag(MapObject):
    type: Literal['finish_flag'] = 'finish_flag'

class StartFlag(MapObject):
    type: Literal['start_flag'] = 'start_flag'

class PlayerCamera(BaseModel):
    position: Position = Field(exclude=True)
    angle: float = Field(exclude=True)
    speed: float = Field(exclude=True)
    view_width: int = 640
    view_height: int = 540
    view_buffer: int = 20

    # This will be set when the player is initialized
    player: Optional['PlayerObject'] = Field(default=None, exclude=True)

class PlayerObject(MapObject):
    type: Literal['player'] = 'player'
    id: int = Field(default=None, exclude=True)
    color: str
    speed: float
    angle: float
    connection: Optional[ServerConnection] = Field(default=None, exclude=True)
    camera: PlayerCamera = Field(default=None, exclude=True)

    # Required for the connection
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def handle_input(self, input: Literal['left', 'right']):
        if input == 'left':
            self.angle = max(45, self.angle + 15)
        elif input == 'right':
            self.angle = min(-45, self.angle - 15)

        return True
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.camera = PlayerCamera(
            position=self.position,
            angle=self.angle,
            speed=self.speed,
            player=self,
        )
    
    
class GameParameters(BaseModel):
    width: int = 3000
    height: int = 20000
    object_start_offset: float = 200 # No obstacles should be generated near the start
    finish_line_offset: float = 100 # The space after the finish flags
    player_start_distance: float = 20
    n_obstacles: int = 5000
    n_powerups: int = 500

    # Physics
    acceleration: float = 9.8
    slope: float = 0.1
    friction: float = 0.1
    air_resistance: float = 0.1
