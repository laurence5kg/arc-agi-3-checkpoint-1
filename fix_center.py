with open('agent.py', 'r', encoding='utf-8') as f:
    text = f.read()

target = '''            # Nodes that intersect with the target bounding box
            goal_nodes = set()
            for (uy, ux) in self.V:
                # Check rectangle intersection between agent footprint at (uy, ux) and target
                if not (uy > t_max_y or uy + h - 1 < t_min_y or ux > t_max_x or ux + w - 1 < t_min_x):
                    goal_nodes.add((uy, ux))'''

repl = '''            # We want to reach the CENTER of the target
            goal_nodes = set()
            t_cy = (t_min_y + t_max_y) // 2
            t_cx = (t_min_x + t_max_x) // 2
            
            # Find the node in V closest to the target center
            best_dist = float('inf')
            best_node = None
            for (uy, ux) in self.V:
                # agent center
                acy = uy + h // 2
                acx = ux + w // 2
                dist = abs(acy - t_cy) + abs(acx - t_cx)
                if dist < best_dist:
                    best_dist = dist
                    best_node = (uy, ux)
            if best_node:
                goal_nodes.add(best_node)'''

if target in text:
    text = text.replace(target, repl)
    with open('agent.py', 'w', encoding='utf-8') as f:
        f.write(text)
    print("Fixed goal_nodes to center!")
