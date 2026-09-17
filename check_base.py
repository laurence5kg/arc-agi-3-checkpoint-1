with open('.venv/Lib/site-packages/arc_agi/base.py', 'r') as f:
    lines = f.readlines()
for i in range(255, 275):
    print(f"{i}: {lines[i]}", end='')
