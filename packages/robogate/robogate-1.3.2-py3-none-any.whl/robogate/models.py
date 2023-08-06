from enum import Enum
from dataclasses import dataclass
from typing import Optional, List, Dict, Any


class ActionType(Enum):
    SHOOT_HEAVY = "ShootHeavy"
    SHOOT_LIGHT = "ShootLight"
    TURN = "Turn"
    FORWARD = "Forward"
    BACKWARD = "Backward"


@dataclass
class Action:
    action_type: ActionType
    # Forward, Backward, Turn
    value: Optional[int] = None


@dataclass
class PlayerAction:
    action: Action
    player_id: str


class CurrentState(Enum):
    DONE = "Done"
    RUNNING = "Running"
    TIMEOUT = "TimeOut"


class EntityType(Enum):
    EXPLOSION = "Explosion"
    HEAVY_BULLET = "HeavyBullet"
    LIGHT_BULLET = "LightBullet"


@dataclass
class Entity:
    owner: str
    entity_type: EntityType
    id: str
    x: float
    y: float
    # LightBullet, HeavyBullet
    direction: Optional[float] = None
    # HeavyBullet
    ticks_to_explosion: Optional[int] = None
    # Explosion
    explosion_step: Optional[int] = None


@dataclass
class Player:
    id: str
    name: str
    x: float
    y: float
    direction: float
    horizontal_speed: float
    vertical_speed: float
    health: int
    light_ammo: int
    heavy_ammo: int
    ticks_until_light_ammo: List[int]
    ticks_until_heavy_ammo: List[int]
    ticks_of_cooldown: int


class EventType(Enum):
    PLAYER_ENTITY_HIT = "PlayerEntityHit"
    PLAYER_COLLISION = "PlayerCollision"
    PLAYER_OUT_OF_BOUNDS = "PlayerOutOfBounds"


@dataclass
class Event:
    event_type: EventType
    # PlayerCollision
    first_id: Optional[str] = None
    second_id: Optional[str] = None
    # PlayerEntityHit, PlayerOutOfBounds
    player_id: Optional[str] = None
    # PlayerEntityHit
    entity_id: Optional[str] = None
    # PlayerOutOfBounds
    horizontal_out: Optional[bool] = None
    vertical_out: Optional[bool] = None


@dataclass
class GameState:
    game_tick: int
    players: Dict[str, Player]
    entities: List[Entity]
    actions: List[PlayerAction]
    events: List[Event]
    current_state: CurrentState

@dataclass
class PlayerInit:
    name: str