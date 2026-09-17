import numpy as np
import sys
sys.path.insert(0, '.')
from envs.arcenv import ARCEnv

env = ARCEnv('../environment_files/ls20', '9607627b')
grid1, _ = env.reset(level=0)
grid2, _, _, _ = env.step(4) # ACTION4 (UP)
M = (grid1 != grid2)
print("Changed pixels after normal step (step counter):", np.sum(M))

# Now trigger the rotation changer at (19, 30) arcengine -> col=19, row=30
# Start is at row=40, col=34. UP x2 -> row=30, col=34. LEFT x3 -> row=30, col=19
env.reset(level=0)
env.step(4)
env.step(4)
env.step(3)
grid_before, _, _, _ = env.step(3)
grid_after, _, _, _ = env.step(3) # Moves into (30, 19)

M = (grid_before != grid_after)
print("Changed pixels after hitting rotation changer:", np.sum(M))
