import os

with open('agent.py', 'r', encoding='utf-8') as f:
    code = f.read()

target = """                        if getattr(self, 'agent_pos', None) == getattr(self, 'last_expected_pos', None):
                            # It arrived normally and didn't trigger any mechanic!
                            if not hasattr(self, 'ignored_targets_by_level'):
                                self.ignored_targets_by_level = {}
                            curr_lvl = getattr(self, 'levels_completed', 0)
                            if curr_lvl not in self.ignored_targets_by_level:
                                self.ignored_targets_by_level[curr_lvl] = set()
                            self.ignored_targets_by_level[curr_lvl].add((t_min_y, t_min_x))
                            # logger is global
                            logger.info(f"Target at {t_min_y, t_min_x} did not react. Ignoring it for level {curr_lvl}.")
                            self.current_path = []"""

replacement = """                        if getattr(self, 'agent_pos', None) == getattr(self, 'last_expected_pos', None):
                            # It arrived normally. BUT did the environment react? (e.g. HUD update)
                            reacted = False
                            if getattr(self, 'last_grid', None) is not None:
                                changed_mask = (current_grid != self.last_grid)
                                # Mask out agent footprint (old and new) to ignore physical moves
                                if getattr(self, 'last_agent_pos', None):
                                    ay, ax = self.last_agent_pos
                                    changed_mask[ay:ay+5, ax:ax+5] = False
                                if getattr(self, 'agent_pos', None):
                                    ay, ax = self.agent_pos
                                    changed_mask[ay:ay+5, ax:ax+5] = False
                                    
                                from scipy.ndimage import label
                                labeled_array, num_features = label(changed_mask)
                                if num_features > 0:
                                    max_cc_size = max((labeled_array == i).sum() for i in range(1, num_features + 1))
                                    if max_cc_size > 15:
                                        reacted = True
                            
                            if not reacted:
                                if not hasattr(self, 'ignored_targets_by_level'):
                                    self.ignored_targets_by_level = {}
                                curr_lvl = getattr(self, 'levels_completed', 0)
                                if curr_lvl not in self.ignored_targets_by_level:
                                    self.ignored_targets_by_level[curr_lvl] = set()
                                self.ignored_targets_by_level[curr_lvl].add((t_min_y, t_min_x))
                                logger.info(f"Target at {t_min_y, t_min_x} did not react. Ignoring it for level {curr_lvl}.")
                                self.current_path = []
                            else:
                                logger.info(f"Target at {t_min_y, t_min_x} REACTED (HUD/env update)! Not ignoring.")
                                # Clear ignored targets since state changed
                                self.ignored_targets_by_level[getattr(self, 'levels_completed', 0)] = set()
                                self.current_path = []"""

if target in code:
    code = code.replace(target, replacement)
    with open('agent.py', 'w', encoding='utf-8') as f:
        f.write(code)
    print('Successfully patched agent.py')
else:
    print('Target not found in agent.py')
