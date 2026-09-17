import re
with open(r'D:\arc-prize-2026-arc-agi-3\environment_files\ls20\9607627b\ls20.py', 'r') as f:
    text = f.read()
level2 = text.split('Level(')[3]
print(set(re.findall(r'sprites\["([a-z]+)"\]', level2)))
