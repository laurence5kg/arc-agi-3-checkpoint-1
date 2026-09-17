with open('agent.py', 'r') as f:
    text = f.read()

bad = '''        # Environment dynamics verification and tracking
        if self.last_grid is not None and not getattr(self, 'just_finished_calibration', False):
            M = (self.last_grid != current_grid)
            # ignore changes in the non-playable manifold
            if hasattr(self, 'playable_manifold'):
                M = M & self.playable_manifold
            total_changed = np.sum(M)'''

good = '''        # Environment dynamics verification and tracking
        if self.last_grid is not None and not getattr(self, 'just_finished_calibration', False):
            M = (self.last_grid != current_grid)
            # ignore changes in the non-playable manifold
            if hasattr(self, 'playable_manifold'):
                M = M & self.playable_manifold
            total_changed = np.sum(M)
            
            # Check if we took an interaction action and nothing happened
            if getattr(self, 'last_action', None) in [GameAction.ACTION5, GameAction.ACTION6] and total_changed <= 10:
                if getattr(self, 'agent_pos', None) is not None:
                    if not hasattr(self, 'ignored_targets'):
                        self.ignored_targets = set()
                    
                    for t in getattr(self, 'targets', []):
                        t_min_y, t_max_y, t_min_x, t_max_x, _ = t
                        t_cy = (t_min_y + t_max_y) // 2
                        t_cx = (t_min_x + t_max_x) // 2
                        best_node = None
                        best_dist = float('inf')
                        for (uy, ux) in getattr(self, 'V', []):
                            dist = abs(uy - t_cy) + abs(ux - t_cx)
                            if dist < best_dist:
                                best_dist = dist
                                best_node = (uy, ux)
                        if best_node == self.agent_pos:
                            self.ignored_targets.add((t_min_y, t_min_x))
                            logger.info(f"Target at {t_min_y, t_min_x} did not react to {self.last_action.name}. Ignoring it.")
                            self.current_path = [] # Force replan'''

text = text.replace(bad, good)
with open('agent.py', 'w') as f:
    f.write(text)
