with open('agent.py', 'r') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if '{patch_crop}' in line or 'bg={bg}")' in line:
        continue
    new_lines.append(line)

with open('agent.py', 'w') as f:
    f.writelines(new_lines)
print("SUCCESS")
