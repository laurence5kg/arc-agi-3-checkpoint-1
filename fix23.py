with open('agent.py', 'r') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if "if total_changed <= 1000:" in line:
        lines[i] = "                if total_changed <= 1000 and getattr(self, 'agent_pos', None) is not None:\n"
    if "if getattr(self, 'agent_pos', None) is not None:" in line and "if total_changed <=" not in line:
        lines[i] = ""

with open('agent.py', 'w') as f:
    f.writelines(lines)
