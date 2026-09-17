with open('agent.py', 'r') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if "self.build_world_model(current_grid, clear_memory=True)" in line and "environment_changed" in lines[i-1]:
        lines[i] = "                self.build_world_model(current_grid, clear_memory=True)\n"

with open('agent.py', 'w') as f:
    f.writelines(lines)
