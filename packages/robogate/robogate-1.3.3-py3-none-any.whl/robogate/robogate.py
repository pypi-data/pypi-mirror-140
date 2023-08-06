import dataclasses
import enum
import sys
from .robot import Robot
import json
import fileinput


class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        if isinstance(o, enum.Enum):
            return o.value
        return super().default(o)

def start_robot_war(robot: Robot):
    playerId = input()
    init = robot.initialize(playerId)
    print(json.dumps(init, cls=EnhancedJSONEncoder), flush=True)
    for line in fileinput.input():
        print(line, file=sys.stderr, flush=True)
        gameState = json.loads(line)
        actions = robot.get_actions(gameState)
        print(json.dumps(actions, cls=EnhancedJSONEncoder))

