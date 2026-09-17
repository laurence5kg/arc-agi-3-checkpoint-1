import sys

with open('agent.py', 'r') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'self.current_path = []' in line and 'logger.error' in lines[i+1]:
        # Delete lines i to i+3
        del lines[i:i+4]
        break

with open('agent.py', 'w') as f:
    f.writelines(lines)
