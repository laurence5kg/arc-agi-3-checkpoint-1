import sys
import numpy as np
sys.path.insert(0, '.')
from envs.arcenv import ARCEnv

env = ARCEnv('../environment_files/ls20', '9607627b')
grid, _ = env.reset(level=0)

print("Grid around row=30..35, col=19..24")
print(grid[30:35, 19:24])

print("Grid around row=31..34, col=20..23")
print(grid[31:34, 20:23])

