with open('agent.py', 'r') as f:
    text = f.read()

bad = '''                        if is_at_goal:
                            self.ignored_targets.add((t_min_y, t_min_x))
                            logger.info(f"Target at {t_min_y, t_min_x} did not react to {self.last_action.name}. Ignoring it.")
                            self.current_path = []'''

good = '''                        if is_at_goal:
                            if not hasattr(self, 'ignored_targets_by_level'):
                                self.ignored_targets_by_level = {}
                            curr_lvl = getattr(self, 'levels_completed', 0)
                            if curr_lvl not in self.ignored_targets_by_level:
                                self.ignored_targets_by_level[curr_lvl] = set()
                            self.ignored_targets_by_level[curr_lvl].add((t_min_y, t_min_x))
                            logger.info(f"Target at {t_min_y, t_min_x} did not react to {self.last_action.name}. Ignoring it for level {curr_lvl}.")
                            self.current_path = []'''

text = text.replace(bad, good)
with open('agent.py', 'w') as f:
    f.write(text)
print("SUCCESS")
