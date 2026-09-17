import sys

with open('agent.py', 'r') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if line.startswith("            print('DIR(SELF):', dir(self))"):
        lines[i] = "            logger.error('DIR(SELF): ' + str(dir(self)))\n"
        break

with open('agent.py', 'w') as f:
    f.writelines(lines)
