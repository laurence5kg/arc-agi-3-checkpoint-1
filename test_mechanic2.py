import numpy as np
import sys
sys.path.append('..')
from arcengine import *
import importlib.util

spec = importlib.util.spec_from_file_location("ls20", "../environment_files/ls20/9607627b/ls20.py")
ls20 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ls20)

for name in dir(ls20):
    if not name.startswith('_'):
        obj = getattr(ls20, name)
        if type(obj) == type and hasattr(obj, 'get_grid'):
            GameClass = obj
            break

game = GameClass(ls20, 0) # Level 0
game.tick(0)
grid1 = game.get_grid().copy()

# Move UP
action = GameAction(GameAction.ACTION4)
game.step(action)
game.tick(0)
grid2 = game.get_grid().copy()

M = (grid1 != grid2)
print("Changed pixels after normal step (step counter & agent):", np.sum(M))

# Reset
game = GameClass(ls20, 0)
game.tick(0)
game.step(GameAction(GameAction.ACTION4))
game.step(GameAction(GameAction.ACTION4))
game.step(GameAction(GameAction.ACTION3))
game.step(GameAction(GameAction.ACTION3))
game.tick(0)
grid_before = game.get_grid().copy()

game.step(GameAction(GameAction.ACTION3))
game.tick(0)
grid_after = game.get_grid().copy()

M = (grid_before != grid_after)
print("Changed pixels after hitting rotation changer (step counter, agent, HUD):", np.sum(M))
