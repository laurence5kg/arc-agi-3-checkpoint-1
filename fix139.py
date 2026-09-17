import re

with open('agent.py', 'r', encoding='utf-8') as f:
    code = f.read()

pattern = r"(logger\.warning\(f\"Agent collision detected\! Expected \{expected_pos\}, got \{self\.agent_pos\}\. Pruned edge\.\"\)\s*if not hasattr\(self, 'pruned_edges'\): self\.pruned_edges = set\(\)\s*self\.pruned_edges\.add\(\(\(ay, ax\), self\.last_action\.name\)\)\s*self\.current_path = \[\])"

replacement = r"""\1
                                  
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
                                          logger.warning(f"Target at {_t_min_y, _t_min_x} rejected agent. Ignoring it.")"""

if re.search(pattern, code):
    code = re.sub(pattern, replacement, code)
    with open('agent.py', 'w', encoding='utf-8') as f:
        f.write(code)
    print("Successfully patched agent.py")
else:
    print("Target not found in agent.py")
