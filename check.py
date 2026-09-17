with open('agent.py', 'r', encoding='utf-8') as f:
    text = f.read()

target = '''        # 1. Update the world model if we moved or it's the first frame
        if self.last_grid is None:
            self.build_world_model(current_grid)
        else:'''

repl = '''        # 1. Update the world model if we moved or it's the first frame
        if self.last_grid is None:
            self.build_world_model(current_grid)
        else:
            # Re-check targets to see if they are blocking our path
            pass'''

if target in text:
    print("Found insertion point")
