import re
with open('run_output24.txt', 'r', encoding='utf-16') as f:
    lines = f.readlines()
for i, line in enumerate(lines):
    if '01:04:07,176' in line:
        for j in range(i, i+600):
            if 'ls20 - ACTION' in lines[j] or 'Finding path from' in lines[j]:
                print(lines[j].strip())
        break
