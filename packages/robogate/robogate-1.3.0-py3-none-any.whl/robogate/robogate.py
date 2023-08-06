import dataclasses
import readline
import sys
from .robot import Robot
import json
import fileinput


class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        return super().default(o)

def start_robot_war(robot: Robot):
    playerId = input()
    init = robot.initialize(playerId)
    print(json.dumps(init, cls=EnhancedJSONEncoder))
    for line in fileinput.input():
        print(line, file=sys.stderr)
        gameState = json.loads(input())
        actions = robot.get_actions(gameState)
        print(json.dumps(actions, cls=EnhancedJSONEncoder))

