with open('agent.py', 'r') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if line.strip() == "patch = self.agent_footprint":
        lines.insert(i, "            if getattr(self, 'agent_pos', None) is not None:\n")
        break

with open('agent.py', 'w') as f:
    f.writelines(lines)
