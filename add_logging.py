with open('agent.py', 'r', encoding='utf-8') as f:
    text = f.read()

target = '''        target_paths = []
        for (t_min_y, t_max_y, t_min_x, t_max_x, color) in self.targets:
            # Nodes that intersect with the target bounding box
            goal_nodes = set()
            for (uy, ux) in self.V:
                # Check rectangle intersection between agent footprint at (uy, ux) and target
                if not (uy > t_max_y or uy + h - 1 < t_min_y or ux > t_max_x or ux + w - 1 < t_min_x):
                    goal_nodes.add((uy, ux))
            
            if goal_nodes:
                path = self.astar(self.agent_pos, goal_nodes)'''

repl = '''        target_paths = []
        for (t_min_y, t_max_y, t_min_x, t_max_x, color) in self.targets:
            # Nodes that intersect with the target bounding box
            goal_nodes = set()
            for (uy, ux) in self.V:
                # Check rectangle intersection between agent footprint at (uy, ux) and target
                if not (uy > t_max_y or uy + h - 1 < t_min_y or ux > t_max_x or ux + w - 1 < t_min_x):
                    goal_nodes.add((uy, ux))
            
            logger.info(f"Target at y=[{t_min_y},{t_max_y}] x=[{t_min_x},{t_max_x}] color={color} -> goal_nodes: {goal_nodes}")
            if goal_nodes:
                path = self.astar(self.agent_pos, goal_nodes)
                logger.info(f"A* path to {goal_nodes}: {path}")'''

if target in text:
    text = text.replace(target, repl)
    with open('agent.py', 'w', encoding='utf-8') as f:
        f.write(text)
    print("Injected logging!")
else:
    print("Could not find block!")
