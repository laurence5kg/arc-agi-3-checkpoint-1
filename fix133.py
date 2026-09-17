with open('agent.py', 'r') as f:
    text = f.read()

bad = '''                if old_patch is not None:
                    if not np.array_equal(old_patch, new_patch):
                        logger.warning("Agent footprint changed (color/rotation)! Clearing pruned edges.")
                        self.pruned_edges = set()'''

good = '''                if old_patch is not None:
                    if not np.array_equal(old_patch, new_patch):
                        logger.warning("Agent footprint changed (color/rotation)! Clearing pruned edges and ignored targets.")
                        self.pruned_edges = set()
                        curr_lvl = getattr(self, 'levels_completed', 0)
                        if hasattr(self, 'ignored_targets_by_level') and curr_lvl in self.ignored_targets_by_level:
                            self.ignored_targets_by_level[curr_lvl].clear()'''

if bad in text:
    text = text.replace(bad, good)
    with open('agent.py', 'w') as f:
        f.write(text)
    print("Fixed ignored_targets clearing!")
else:
    print("Could not find block!")
