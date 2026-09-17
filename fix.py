import sys

with open('agent.py', 'r') as f:
    lines = f.readlines()

start_idx = -1
end_idx = -1
for i, line in enumerate(lines):
    if line.startswith('        if getattr(self, \'agent_pos\', None) is not None:'):
        if 'patch = self.agent_footprint' in lines[i+1]:
            start_idx = i
            break

if start_idx != -1:
    for i in range(start_idx, len(lines)):
        if line.startswith('        if not hasattr(self, \'current_path\') or not self.current_path or getattr(self, \'environment_changed\', False):'):
            end_idx = i
            break
        line = lines[i]

print(start_idx, end_idx)
