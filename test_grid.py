import numpy as np
import sys
sys.path.append('.')

import importlib.util
spec = importlib.util.spec_from_file_location("ls20", "../environment_files/ls20/9607627b/ls20.py")
ls20 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ls20)

for name in dir(ls20):
    if not name.startswith('_'):
        obj = getattr(ls20, name)
        if type(obj) == type and hasattr(obj, 'get_grid'):
            game = obj(ls20)
            break

game.tick(0)
grid = game.get_grid()
print("Grid around row=30..35, col=19..24")
print(grid[30:35, 19:24])
