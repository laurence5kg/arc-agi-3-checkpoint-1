import os

with open('agent.py', 'r', encoding='utf-8') as f:
    code = f.read()

target = """                                  logger.warning(f"Agent collision detected! Expected {expected_pos}, got {self.agent_pos}. Pruned edge.")
                                  if not hasattr(self, 'pruned_edges'): self.pruned_edges = set()
                                  self.pruned_edges.add(((ay, ax), self.last_action.name))
                                  self.current_path = []"""

replacement = """                                  logger.warning(f"Agent collision detected! Expected {expected_pos}, got {self.agent_pos}. Pruned edge.")
                                  if not hasattr(self, 'pruned_edges'): self.pruned_edges = set()
                                  self.pruned_edges.add(((ay, ax), self.last_action.name))
                                  self.current_path = []
                                  
                                  # If expected_pos overlaps a target, it rejected us! Ignore it.
                                  for t in getattr(self, 'targets', []):
                                      t_min_y, t_max_y, t_min_x, t_max_x, _ = t
                                      ey, ex = expected_pos
                                      if t_min_y <= ey <= t_max_y and t_min_x <= ex <= t_max_x:
                                          curr_lvl = getattr(self, 'levels_completed', 0)
                                          if not hasattr(self, 'ignored_targets_by_level'):
                                              self.ignored_targets_by_level = {}
                                          if curr_lvl not in self.ignored_targets_by_level:
                                              self.ignored_targets_by_level[curr_lvl] = set()
                                          self.ignored_targets_by_level[curr_lvl].add((t_min_y, t_min_x))
                                          logger.warning(f"Target at {t_min_y, t_min_x} rejected agent (acted as wall). Ignoring it.")"""

if target in code:
    code = code.replace(target, replacement)
    with open('agent.py', 'w', encoding='utf-8') as f:
        f.write(code)
    print("Successfully patched agent.py")
else:
    print("Target not found in agent.py")
