from abc import ABC, abstractmethod
from typing import List

from .models import Action, GameState, PlayerInit

class Robot(ABC):
    
    @abstractmethod
    def initialize(self, playerId: str) -> PlayerInit:
        pass

    @abstractmethod
    def get_actions(self, state: GameState) -> List[Action]:
        pass