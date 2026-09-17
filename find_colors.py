with open(r'D:\arc-prize-2026-arc-agi-3\environment_files\ls20\9607627b\ls20.py', 'r') as f:
    text = f.read()
level2 = text.split('Level(')[3].split('Level(')[0]

import re
matches = re.findall(r'StartColor\s*=\s*(\d+)', level2)
print("Colors in Level 2:", set(matches))
