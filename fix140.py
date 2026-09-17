import re

with open('agent.py', 'r', encoding='utf-8') as f:
    code = f.read()

# We just remove the bad lines and re-insert correctly
code = re.sub(
    r"\s*for _t in getattr\(self, 'targets', \[\]\):.*?(?=else:\n\s*self\.agent_pos = None)",
    "",
    code,
    flags=re.DOTALL
)

insertion = """
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
                                          logger.warning(f"Target at {_t_min_y}, {_t_min_x} rejected agent. Ignoring it.")
"""

code = code.replace("self.current_path = []", "self.current_path = []" + insertion)

with open('agent.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("Fixed indent.")
