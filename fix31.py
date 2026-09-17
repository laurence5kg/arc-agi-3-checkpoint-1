with open('agent.py', 'r') as f:
    text = f.read()

bad = '''                    self.last_grid = current_grid
                    self.build_world_model(current_grid, clear_memory=True)'''

good = '''                    self.last_grid = current_grid
                    self.build_world_model(current_grid, clear_memory=False)'''

if bad in text:
    text = text.replace(bad, good)
    print("SUCCESS")
else:
    print("FAILED")
with open('agent.py', 'w') as f:
    f.write(text)
