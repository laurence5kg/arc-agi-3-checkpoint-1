with open('agent.py', 'r') as f:
    text = f.read()

bad = '''        if self.current_path:
            action_name = self.current_path.pop(0)
            self.last_action = GameAction[action_name]
            self.last_grid = current_grid
            return self.last_action
        else:
            # We have no path, maybe target is unreachable? Or we are stuck.
            # Try to force a change by cycling actions 1-6.
            actions = [GameAction.ACTION1, GameAction.ACTION2, GameAction.ACTION3, GameAction.ACTION4, GameAction.ACTION5, GameAction.ACTION6]
            idx = actions.index(getattr(self, 'last_action', GameAction.ACTION1)) if getattr(self, 'last_action', None) in actions else -1
            next_action = actions[(idx + 1) % len(actions)]
            self.last_action = next_action
            self.last_grid = current_grid
            return next_action'''

good = '''        if self.current_path:
            action_name = self.current_path.pop(0)
            self.last_action = GameAction[action_name]
            self.last_grid = current_grid
            return self.last_action
        else:
            if getattr(self, 'last_action', None) in [GameAction.ACTION5, GameAction.ACTION6]:
                if self.last_grid is not None and np.array_equal(self.last_grid, current_grid):
                    if getattr(self, 'agent_pos', None) is not None:
                        if not hasattr(self, 'ignored_targets'):
                            self.ignored_targets = set()
                        for t in getattr(self, 'targets', []):
                            t_min_y, t_max_y, t_min_x, t_max_x, _ = t
                            t_cy = (t_min_y + t_max_y) // 2
                            t_cx = (t_min_x + t_max_x) // 2
                            best_node = None
                            best_dist = float('inf')
                            for (uy, ux) in self.V:
                                dist = abs(uy - t_cy) + abs(ux - t_cx)
                                if dist < best_dist:
                                    best_dist = dist
                                    best_node = (uy, ux)
                            if best_node == self.agent_pos:
                                self.ignored_targets.add((t_min_y, t_min_x))
                                logger.info(f"Target at {t_min_y, t_min_x} did not react. Ignoring it.")
            
            actions = [GameAction.ACTION5, GameAction.ACTION6]
            if getattr(self, 'last_action', None) == GameAction.ACTION6:
                actions = [GameAction.ACTION1, GameAction.ACTION2, GameAction.ACTION3, GameAction.ACTION4]
            
            idx = actions.index(getattr(self, 'last_action', GameAction.ACTION1)) if getattr(self, 'last_action', None) in actions else -1
            next_action = actions[(idx + 1) % len(actions)]
            self.last_action = next_action
            self.last_grid = current_grid
            return next_action'''

text = text.replace(bad, good)
with open('agent.py', 'w') as f:
    f.write(text)
