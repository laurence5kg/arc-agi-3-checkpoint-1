import re

with open('agent.py', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Remove all the bad insertions
bad_insertion = r"\s*for _t in getattr\(self, 'targets', \[\]\):\s*_t_min_y, _t_max_y, _t_min_x, _t_max_x, _ = _t\s*_ey, _ex = expected_pos\s*if _t_min_y <= _ey <= _t_max_y and _t_min_x <= _ex <= _t_max_x:\s*_curr_lvl = getattr\(self, 'levels_completed', 0\)\s*if not hasattr\(self, 'ignored_targets_by_level'\):\s*self\.ignored_targets_by_level = \{\}\s*if _curr_lvl not in self\.ignored_targets_by_level:\s*self\.ignored_targets_by_level\[_curr_lvl\] = set\(\)\s*self\.ignored_targets_by_level\[_curr_lvl\]\.add\(\(_t_min_y, _t_min_x\)\)\s*logger\.warning\(f\"Target at \{_t_min_y\}, \{_t_min_x\} rejected agent\. Ignoring it\.\"\)"
code = re.sub(bad_insertion, "", code)

# 2. Insert it at the correct place
target = """                                  logger.warning(f"Agent collision detected! Expected {expected_pos}, got {self.agent_pos}. Pruned edge.")
                                  if not hasattr(self, 'pruned_edges'): self.pruned_edges = set()
                                  self.pruned_edges.add(((ay, ax), self.last_action.name))
                                  self.current_path = []"""

replacement = """                                  logger.warning(f"Agent collision detected! Expected {expected_pos}, got {self.agent_pos}. Pruned edge.")
                                  if not hasattr(self, 'pruned_edges'): self.pruned_edges = set()
                                  self.pruned_edges.add(((ay, ax), self.last_action.name))
                                  self.current_path = []
                                  
                                  for _t in getattr(self, 'targets', []):
                                      _t_min_y, _t_max_y, _t_min_x, _t_max_x, _ = _t
                                      _ey, _ex = expected_pos
                                      if _t_min_y <= _ey <= _t_max_y and _t_min_x <= _ex <= _t_max_x:
                                          _curr_lvl = getattr(self, 'levels_completed', 0)
                                          if not hasattr(self, 'ignored_targets_by_level'):
                                              self.ignored_targets_by_level = {}
                                          if _curr_lvl not in self.ignored_targets_by_level:
                                              self.ignored_targets_by_level[_curr_lvl] = set()
                                          self.ignored_targets_by_level[_curr_lvl].add((_t_min_y, _t_min_x))
                                          logger.warning(f"Target at {_t_min_y}, {_t_min_x} rejected agent. Ignoring it.")"""

if target in code:
    code = code.replace(target, replacement)
    with open('agent.py', 'w', encoding='utf-8') as f:
        f.write(code)
    print("Successfully patched agent.py")
else:
    print("Target not found in agent.py")
