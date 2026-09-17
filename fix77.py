with open('agent.py', 'r') as f:
    text = f.read()

bad = '''        if not hasattr(self, 'ignored_targets'):
            self.ignored_targets = set()
            
        target_paths = []
        for (t_min_y, t_max_y, t_min_x, t_max_x, color) in self.targets:
            if (t_min_y, t_min_x) in self.ignored_targets:'''

good = '''        if not hasattr(self, 'ignored_targets_by_level'):
            self.ignored_targets_by_level = {}
        curr_lvl = getattr(self, 'levels_completed', 0)
        ignored_targets = self.ignored_targets_by_level.get(curr_lvl, set())
            
        target_paths = []
        for (t_min_y, t_max_y, t_min_x, t_max_x, color) in self.targets:
            if (t_min_y, t_min_x) in ignored_targets:'''

text = text.replace(bad, good)
with open('agent.py', 'w') as f:
    f.write(text)
print("SUCCESS")
