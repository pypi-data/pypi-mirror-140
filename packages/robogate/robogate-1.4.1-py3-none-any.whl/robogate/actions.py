from .models import Action, ActionType


class Forward(Action):
    def __init__(self, power = 1):
        self.action_type = ActionType.FORWARD
        self.value = power

class Backward(Action):
    def __init__(self, power = 1):
        self.action_type = ActionType.BACKWARD
        self.value = power

class Turn(Action):
    def __init__(self, power = 0):
        self.action_type = ActionType.TURN
        self.value = power

class ShootLight(Action):
    def __init__(self):
        self.action_type = ActionType.SHOOT_LIGHT

class ShootHeavy(Action):
    def __init__(self):
        self.action_type = ActionType.SHOOT_HEAVY