import re

with open('agent.py', 'r', encoding='utf-8') as f:
    code = f.read()

pattern = r"(for t in getattr\(self, 'targets', \[\]\):\s*t_min_y, t_max_y, t_min_x, t_max_x, _ = t\s*if not \(amax_y < t_min_y or amin_y > t_max_y or amax_x < t_min_x or amin_x > t_max_x\):)\s*# Overlaps! Check if it was a normal move\s*if getattr\(self, 'agent_pos', None\) == getattr\(self, 'last_expected_pos', None\):"

replacement = r"""\1
                          # Calculate overlap area to avoid 1-pixel edge touches (e.g. ls20 adjacencies)
                          iy_min = max(amin_y, t_min_y)
                          iy_max = min(amax_y, t_max_y)
                          ix_min = max(amin_x, t_min_x)
                          ix_max = min(amax_x, t_max_x)
                          overlap_area = max(0, iy_max - iy_min + 1) * max(0, ix_max - ix_min + 1)
                          
                          # Most targets are 5x5 (25). Require at least 4 pixels of overlap.
                          if overlap_area < 4:
                              continue
                              
                          # Overlaps! Check if it was a normal move
                          if getattr(self, 'agent_pos', None) == getattr(self, 'last_expected_pos', None):"""

if re.search(pattern, code):
    code = re.sub(pattern, replacement, code)
    with open('agent.py', 'w', encoding='utf-8') as f:
        f.write(code)
    print("Successfully patched agent.py")
else:
    print("Target not found in agent.py")
