with open('agent.py', 'r') as f:
    text = f.read()

bad1 = '''        if getattr(latest_frame, 'state', None) == GameState.GAME_OVER:
            logger.warning("Game is OVER! Returning RESET.")
            if getattr(self, 'current_target', None) is not None:
                if not hasattr(self, 'ignored_targets_by_level'):
                    self.ignored_targets_by_level = {}
                curr_lvl = getattr(self, 'levels_completed', 0)
                if curr_lvl not in self.ignored_targets_by_level:
                    self.ignored_targets_by_level[curr_lvl] = set()
                t_min_y, t_max_y, t_min_x, t_max_x, color = self.current_target
                self.ignored_targets_by_level[curr_lvl].add((t_min_y, t_min_x))
                logger.warning(f"Added dead-end target to ignored_targets for level {curr_lvl}: {self.current_target}")
                self.current_target = None
                self.current_path = []'''

good1 = '''        if getattr(latest_frame, 'state', None) == GameState.GAME_OVER:
            logger.warning("Game is OVER! Returning RESET.")
            
            if getattr(self, 'agent_pos', None) is not None and getattr(self, 'last_action', None) is not None:
                d_y, d_x = self.action_mapping.get(self.last_action.name, (0, 0))
                p_y, p_x = self.agent_pos
                deadly_y, deadly_x = p_y + d_y, p_x + d_x
                if not hasattr(self, 'deadly_nodes_by_level'):
                    self.deadly_nodes_by_level = {}
                curr_lvl = getattr(self, 'levels_completed', 0)
                if curr_lvl not in self.deadly_nodes_by_level:
                    self.deadly_nodes_by_level[curr_lvl] = set()
                self.deadly_nodes_by_level[curr_lvl].add((deadly_y, deadly_x))
                logger.warning(f"Added DEADLY NODE to memory for level {curr_lvl}: {(deadly_y, deadly_x)}")
            
            if getattr(self, 'current_target', None) is not None:
                self.current_target = None
                self.current_path = []'''

text = text.replace(bad1, good1)

bad2 = '''                    for neighbor in self.get_neighbors(current):
                        if getattr(self, 'pruned_edges', None) and (current, neighbor) in self.pruned_edges:
                            continue'''

good2 = '''                    for neighbor in self.get_neighbors(current):
                        if getattr(self, 'pruned_edges', None) and (current, neighbor) in self.pruned_edges:
                            continue
                        if getattr(self, 'deadly_nodes_by_level', None):
                            curr_lvl = getattr(self, 'levels_completed', 0)
                            if neighbor in self.deadly_nodes_by_level.get(curr_lvl, set()):
                                continue'''

text = text.replace(bad2, good2)
with open('agent.py', 'w') as f:
    f.write(text)
print("SUCCESS")
