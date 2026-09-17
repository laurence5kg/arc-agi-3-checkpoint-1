import sys; sys.path.append('../environment_files/ls20/9607627b'); import ls20;
env = ls20.Ls20()
env.reset()
import numpy as np
grid = np.array(env.render())
perimeter = np.concatenate([
    grid[0, :], grid[-1, :],
    grid[1:-1, 0], grid[1:-1, -1]
])
wall_color = int(np.argmax(np.bincount(perimeter)))
print("wall_color is:", wall_color)
from collections import Counter
print(Counter(perimeter))
