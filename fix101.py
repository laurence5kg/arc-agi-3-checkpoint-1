with open('agent.py', 'r') as f:
    text = f.read()

bad = '''            if getattr(self, 'last_grid', None) is not None and not np.array_equal(current_grid, self.last_grid):
                d, R = self.discover_semantics(self.last_grid, current_grid, known_patch=None)'''

good = '''            if getattr(self, 'last_grid', None) is not None and not np.array_equal(current_grid, self.last_grid):
                kp = self.agent_footprint[4] if hasattr(self, 'agent_footprint') and self.agent_footprint else None
                d, R = self.discover_semantics(self.last_grid, current_grid, known_patch=kp)'''

if bad in text:
    text = text.replace(bad, good)
    with open('agent.py', 'w') as f:
        f.write(text)
    print("Fixed known_patch!")
else:
    print("Could not find block!")
