import numpy as np
import importlib.util
import sys

try:
    from arcengine import GameAction
except Exception as e:
    print(e)

spec = importlib.util.spec_from_file_location("ls20", "../environment_files/ls20/9607627b/ls20.py")
ls20 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ls20)

for name in dir(ls20):
    if not name.startswith('_'):
        obj = getattr(ls20, name)
        if type(obj) == type and hasattr(obj, 'get_grid'):
            GameClass = obj
            break

print("GameClass:", GameClass)
game = GameClass() # It takes no args in __init__, but it calls setup()

grid1 = game.get_grid().copy()

action = GameAction(GameAction.ACTION4)
game.step(action)
grid2 = game.get_grid().copy()

M = (grid1 != grid2)
print("Changed pixels after normal step (step counter & agent):", np.sum(M))

game = GameClass()
game.step(GameAction(GameAction.ACTION4))
game.step(GameAction(GameAction.ACTION4))
game.step(GameAction(GameAction.ACTION3))
game.step(GameAction(GameAction.ACTION3))
grid_before = game.get_grid().copy()

game.step(GameAction(GameAction.ACTION3))
grid_after = game.get_grid().copy()

M = (grid_before != grid_after)
print("Changed pixels after hitting rotation changer (step counter, agent, HUD):", np.sum(M))
