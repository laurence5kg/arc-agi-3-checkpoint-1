import re

with open('agent.py', 'r', encoding='utf-8') as f:
    code = f.read()

target = """                    if self._check_patch_at(current_grid, self.agent_footprint, (ay, ax)):"""
replacement = """                    if self._check_patch_at(current_grid, self.agent_footprint, (ay, ax)) or np.sum(current_grid == 2) > (current_grid.shape[0]*current_grid.shape[1]*0.8):"""

if target in code:
    code = code.replace(target, replacement)
    with open('agent.py', 'w', encoding='utf-8') as f:
        f.write(code)
    print("Successfully patched agent.py")
else:
    print("Target not found in agent.py")
