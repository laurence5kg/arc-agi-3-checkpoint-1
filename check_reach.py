import sys; sys.path.append('../environment_files/ls20/9607627b'); import ls20;
from arc_agi.base import GameAction
env = ls20.ARCEnvironment()
env.reset()
# Beat level 1
# Need to execute actions to beat level 1
print("Level 1 start rot:", env.cklxociuu)
env.take_action(GameAction.ACTION1) # and see what it does
