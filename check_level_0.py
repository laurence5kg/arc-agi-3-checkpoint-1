import sys
sys.path.append('.')
from envs.arcenv import ARCEnv

env = ARCEnv('../environment_files/ls20', '9607627b')
grid, _ = env.reset(level=0)
print(grid.shape)
import numpy as np
for i in range(grid.shape[0]):
    for j in range(grid.shape[1]):
        if grid[i, j] == 0:
            print(f"Color 0 at: row={i}, col={j}")
