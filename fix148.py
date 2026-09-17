import re

with open('agent.py', 'r', encoding='utf-8') as f:
    code = f.read()

target = """                if getattr(self, 'agent_pos', None) is not None:
                    ay, ax = self.agent_pos
                    if self._check_patch_at(current_grid, self.agent_footprint, (ay, ax)) or np.sum(current_grid == 2) > (current_grid.shape[0]*current_grid.shape[1]*0.8):"""

replacement = """                if getattr(self, 'agent_pos', None) is not None:
                    ay, ax = self.agent_pos
                    if getattr(self, 'last_action', None) is not None:
                        dy, dx = self.action_mapping.get(self.last_action.name, (0, 0))
                        if dy != 0 or dx != 0:
                            expected_pos = (ay + dy, ax + dx)
                            for _t in getattr(self, 'targets', []):
                                _t_min_y, _t_max_y, _t_min_x, _t_max_x, _ = _t
                                _ey, _ex = expected_pos
                                _h, _w = self.agent_footprint[2], self.agent_footprint[3]
                                if not (_ey + _h - 1 < _t_min_y or _ey > _t_max_y or _ex + _w - 1 < _t_min_x or _ex > _t_max_x):
                                    _curr_lvl = getattr(self, 'levels_completed', 0)
                                    if not hasattr(self, 'ignored_targets_by_level'):
                                        self.ignored_targets_by_level = {}
                                    if _curr_lvl not in self.ignored_targets_by_level:
                                        self.ignored_targets_by_level[_curr_lvl] = set()
                                    self.ignored_targets_by_level[_curr_lvl].add((_t_min_y, _t_min_x))
                                    logger.warning(f"Target at {_t_min_y}, {_t_min_x} rejected agent (or caused lost tracking). Ignoring it.")
                    
                    if self._check_patch_at(current_grid, self.agent_footprint, (ay, ax)):"""

if target in code:
    code = code.replace(target, replacement)
    with open('agent.py', 'w', encoding='utf-8') as f:
        f.write(code)
    print("Successfully patched agent.py")
else:
    print("Target not found in agent.py")
