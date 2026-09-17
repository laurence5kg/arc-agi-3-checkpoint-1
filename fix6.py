import sys

with open('agent.py', 'r') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if line.startswith('    def choose_action'):
        lines.insert(i+1, "        if not hasattr(self, '_printed_dir'):\n            print('DIR(SELF):', dir(self))\n            self._printed_dir = True\n")
        break

with open('agent.py', 'w') as f:
    f.writelines(lines)
