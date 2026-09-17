with open('agent.py', 'r') as f:
    text = f.read()

bad = '''        # Record current level
        if getattr(latest_frame, 'levels_completed', None) is not None:
            self.levels_completed = latest_frame.levels_completed'''

good = '''        # Record current level
        if getattr(latest_frame, 'levels_completed', None) is not None:
            old_levels = getattr(self, 'levels_completed', 0)
            self.levels_completed = latest_frame.levels_completed
            if self.levels_completed > old_levels:
                self.advanced_level = True'''

text = text.replace(bad, good)
with open('agent.py', 'w') as f:
    f.write(text)
print("SUCCESS")
