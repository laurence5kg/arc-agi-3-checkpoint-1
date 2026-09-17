with open('agent.py', 'r') as f:
    text = f.read()

bad = '''            total_pixels = M.shape[0] * M.shape[1]
            
        if not self.current_path:'''

good = '''            total_pixels = M.shape[0] * M.shape[1]
            
            is_level_transition = (total_changed / total_pixels) > 0.3
            
            if not is_level_transition and getattr(self, 'agent_pos', None) is not None:
                ay, ax = self.agent_pos
                h, w = self.agent_footprint[2], self.agent_footprint[3]
                amin_y, amax_y = ay, ay + h - 1
                amin_x, amax_x = ax, ax + w - 1
                
                for t in getattr(self, 'targets', []):
                    t_min_y, t_max_y, t_min_x, t_max_x, _ = t
                    if not (amax_y < t_min_y or amin_y > t_max_y or amax_x < t_min_x or amin_x > t_max_x):
                        # Overlaps! Check if it was a normal move
                        if getattr(self, 'agent_pos', None) == getattr(self, 'last_expected_pos', None):
                            # It arrived normally and didn't trigger any mechanic!
                            if not hasattr(self, 'ignored_targets_by_level'):
                                self.ignored_targets_by_level = {}
                            curr_lvl = getattr(self, 'levels_completed', 0)
                            if curr_lvl not in self.ignored_targets_by_level:
                                self.ignored_targets_by_level[curr_lvl] = set()
                            self.ignored_targets_by_level[curr_lvl].add((t_min_y, t_min_x))
                            import logging
                            logger = logging.getLogger(__name__)
                            logger.info(f"Target at {t_min_y, t_min_x} did not react. Ignoring it for level {curr_lvl}.")
                            self.current_path = []
            
        if not self.current_path:'''

if bad in text:
    text = text.replace(bad, good)
    with open('agent.py', 'w') as f:
        f.write(text)
    print("Restored ignore logic!")
else:
    print("Could not find block!")
