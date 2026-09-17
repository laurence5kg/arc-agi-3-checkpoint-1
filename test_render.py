import sys
import importlib.util
sys.path.append('.')
spec = importlib.util.spec_from_file_location('ls20', '../environment_files/ls20/9607627b/ls20.py')
ls20_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ls20_module)
game = ls20_module.Ls20()
lvl = game._levels[1]
for i, s in enumerate(lvl._sprites):
    x, y = s.x, s.y
    if x in range(48, 52) and y in range(44, 52):
        print(f'Sprite {i}: x={x}, y={y} name={getattr(s, "name", "")}')
