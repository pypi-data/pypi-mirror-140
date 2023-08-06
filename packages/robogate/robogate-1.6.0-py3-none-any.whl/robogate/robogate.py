import sys
from .robot import Robot
import json
import fileinput


def start_robot_war(robot: Robot):
    playerId = input()
    init = robot.initialize(playerId)
    print(init.to_json(), flush=True)
    for line in fileinput.input():
        print(line, file=sys.stderr, flush=True)
        gameState = json.loads(line)
        actions = robot.get_actions(gameState)
        print('[' + ",".join([action.to_json() for action in actions]) + ']', flush=True)
