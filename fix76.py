with open('agent.py', 'r') as f:
    text = f.read()

bad1 = '''        if clear_memory:
            if hasattr(self, 'pruned_edges'):
                self.pruned_edges.clear()
            logger.info("Level transition: clearing pruned_edges.")
            if getattr(self, 'advanced_level', False):
                logger.info("Advanced to next level! Clearing ignored_targets.")
                old_ignored = set()
                self.advanced_level = False
            else:
                logger.info("Death/Reset transition! KEEPING ignored_targets.")
                old_ignored = getattr(self, 'ignored_targets', set()).copy()
        else:
            old_ignored = getattr(self, 'ignored_targets', set()).copy()'''

good1 = '''        if clear_memory:
            if hasattr(self, 'pruned_edges'):
                self.pruned_edges.clear()
            logger.info("Level transition: clearing pruned_edges.")
        
        if not hasattr(self, 'ignored_targets_by_level'):
            self.ignored_targets_by_level = {}
        curr_lvl = getattr(self, 'levels_completed', 0)
        old_ignored = self.ignored_targets_by_level.get(curr_lvl, set()).copy()'''

text = text.replace(bad1, good1)

bad2 = '''                if not hasattr(self, 'ignored_targets'):
                    self.ignored_targets = set()
                t_min_y, t_max_y, t_min_x, t_max_x, color = self.current_target
                self.ignored_targets.add((t_min_y, t_min_x))
                logger.warning(f"Added dead-end target to ignored_targets: {self.current_target}")'''

good2 = '''                if not hasattr(self, 'ignored_targets_by_level'):
                    self.ignored_targets_by_level = {}
                curr_lvl = getattr(self, 'levels_completed', 0)
                if curr_lvl not in self.ignored_targets_by_level:
                    self.ignored_targets_by_level[curr_lvl] = set()
                t_min_y, t_max_y, t_min_x, t_max_x, color = self.current_target
                self.ignored_targets_by_level[curr_lvl].add((t_min_y, t_min_x))
                logger.warning(f"Added dead-end target to ignored_targets for level {curr_lvl}: {self.current_target}")'''

text = text.replace(bad2, good2)
with open('agent.py', 'w') as f:
    f.write(text)
print("SUCCESS")
