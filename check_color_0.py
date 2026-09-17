import numpy as np
import sys
sys.path.append('..')

import importlib.util
spec = importlib.util.spec_from_file_location("ls20", "../environment_files/ls20/9607627b/ls20.py")
ls20 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ls20)

game = ls20.create_game()
game.tick(0)
grid = game.get_grid().copy()
c0 = np.argwhere(grid == 0)
print(f"Color 0 locations in level 0:")
print(c0)
