import readline
import sys
from .robot import Robot
import json
import fileinput

def start_robot_war(robot: Robot):
    playerId = input()
    init = robot.initialize(playerId)
    print(json.dumps(init))
    for line in fileinput.input():
        print(line, file=sys.stderr)
        gameState = json.loads(input())
        actions = robot.get_actions(gameState)
        print(json.dumps(actions))