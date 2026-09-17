import sys

with open('agent.py', 'r') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if line.startswith('        if getattr(self, \'agent_pos\', None) is None:'):
        # We need to replace lines i to i+4 with just the two lines
        lines[i] = "        if getattr(self, 'agent_pos', None) is None:\n"
        lines[i+1] = "            return getattr(self, 'last_action', GameAction.ACTION1)\n"
        del lines[i+2:i+5]
        break

with open('agent.py', 'w') as f:
    f.writelines(lines)
