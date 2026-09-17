import numpy as np
import importlib.util

from arcengine import GameAction

spec = importlib.util.spec_from_file_location("ls20", "../environment_files/ls20/9607627b/ls20.py")
ls20 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ls20)

GameClass = ls20.Ls20
game = GameClass()
game.setup()
# skip the menu level (Level 0 in arcengine is the thumbnail)
# The actual Level 1 (index 1) is what my agent calls Level 0!
game.next_level()
game.tick(0)
grid1 = game.get_grid().copy()

# Move UP
action = GameAction(GameAction.ACTION4)
game.step(action)
game.tick(0)
grid2 = game.get_grid().copy()

M = (grid1 != grid2)
print("Changed pixels after normal step (step counter & agent):", np.sum(M))

game = GameClass()
game.setup()
game.next_level()
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
