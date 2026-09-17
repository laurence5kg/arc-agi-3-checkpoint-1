import sys
import os
sys.path.append("D:/arc-prize-2026-arc-agi-3/environment_files/ls20/9607627b")
from ls20 import Ls20
import numpy as np

game = Ls20()
game.set_level(1)
game.wbcenorpju()
grid = np.array(game.get_pixels(0, 0, 64, 64))
if grid.ndim == 3: grid = grid[-1]
print("y=45..49, x=39..43:")
print(grid[45:50, 39:44])
print("y=45..49, x=49..53:")
print(grid[45:50, 49:54])
