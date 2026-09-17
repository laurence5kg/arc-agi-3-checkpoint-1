with open('agent.py', 'r', encoding='utf-8') as f:
    text = f.read()

target = '''        # Identify targets
        targets = []
        for i in range(1, num_features + 1):
            if i == manifold_id:
                continue
            
            ys, xs = np.where(labeled_passable == i)
            # Mask out the agent footprint
            t_min_y, t_max_y = ys.min(), ys.max()
            t_min_x, t_max_x = xs.min(), xs.max()
            
            if t_min_y == r_y and t_max_y == r_y + h - 1 and t_min_x == r_x and t_max_x == r_x + w - 1:
                continue'''

repl = '''        # Identify targets
        targets = []
        curr_y, curr_x = getattr(self, 'agent_pos', (r_y, r_x))
        for i in range(1, num_features + 1):
            if i == manifold_id:
                continue
            
            ys, xs = np.where(labeled_passable == i)
            # Mask out the agent footprint
            t_min_y, t_max_y = ys.min(), ys.max()
            t_min_x, t_max_x = xs.min(), xs.max()
            
            if t_min_y == curr_y and t_max_y == curr_y + h - 1 and t_min_x == curr_x and t_max_x == curr_x + w - 1:
                continue'''

if target in text:
    text = text.replace(target, repl)
    with open('agent.py', 'w', encoding='utf-8') as f:
        f.write(text)
    print("Replaced!")
else:
    print("Target not found!")
