with open('agent.py', 'r') as f:
    text = f.read()
bad = '''                self.last_grid = current_grid
                self.build_world_model(current_grid, clear_memory=False)
            else:'''
good = '''                self.last_grid = current_grid
                if not getattr(self, 'calibration_phase', False):
                    self.build_world_model(current_grid, clear_memory=False)
            else:'''
if bad in text:
    text = text.replace(bad, good)
    with open('agent.py', 'w') as f:
        f.write(text)
    print("Fixed build_world_model call!")
else:
    print("Could not find block!")
