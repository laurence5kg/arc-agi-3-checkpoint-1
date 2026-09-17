with open('agent.py', 'r', encoding='utf-8') as f:
    text = f.read()

target = '''        for u in self.V:
            for action_name, d in self.action_mapping.items():
                if d == (0, 0): continue
                if (u, action_name) in self.pruned_edges:
                    continue
                v = (u[0] + d[0], u[1] + d[1])
                if v in self.V:
                    self.E[u][action_name] = v
                    
        total_edges = sum(len(edges) for edges in self.E.values())
        logger.info(f"Filtered Graph: |V|={len(self.V)}, |E|={total_edges}")'''

repl = '''        for u in self.V:
            for action_name, d in self.action_mapping.items():
                if d == (0, 0): continue
                if (u, action_name) in self.pruned_edges:
                    continue
                v = (u[0] + d[0], u[1] + d[1])
                if v in self.V:
                    self.E[u][action_name] = v
                    
        total_edges = sum(len(edges) for edges in self.E.values())
        logger.info(f"Filtered Graph: |V|={len(self.V)}, |E|={total_edges}")
        
        interior_pixels = grid[self.playable_manifold]
        bg_color = int(np.argmax(np.bincount(interior_pixels)))
        
        mask = (grid != bg_color) & (grid != wall_color) & self.playable_manifold
        curr_y, curr_x = getattr(self, 'agent_pos', (r_y, r_x))
        mask[curr_y:curr_y+h, curr_x:curr_x+w] = False
        
        labeled, num_features = label(mask)
        self.targets = []
        for i in range(1, num_features + 1):
            ys, xs = np.where(labeled == i)
            self.targets.append((int(ys.min()), int(ys.max()), int(xs.min()), int(xs.max()), int(grid[ys[0], xs[0]])))
            
        logger.info(f"Target Candidates (Interior Only): {len(self.targets)} found.")'''

if target in text:
    text = text.replace(target, repl)
    with open('agent.py', 'w', encoding='utf-8') as f:
        f.write(text)
    print("Replaced targets!")
else:
    print("Target block not found!")
