from arc_env import ARCEnv
import numpy as np
import enum

class GameAction(enum.Enum):
    RESET = 0
    ACTION1 = 1

env = ARCEnv("D:/arc-prize-2026-arc-agi-3/environment_files/ls20/9607627b")

# Win level 0 (just hack the level)
env.game.levels_completed = 1
env.game.current_level_index = 1
env.game.wbcenorpju()

frame = env.step(GameAction.ACTION1)
grid = np.array(frame.frame)
if grid.ndim == 3: grid = grid[-1]
print("y=40..44, x=34..38:")
print(grid[40:45, 34:39])
