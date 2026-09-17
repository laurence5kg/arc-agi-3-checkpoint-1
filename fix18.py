with open('agent.py', 'r') as f:
    text = f.read()

bad = '''        # Environment dynamics verification and tracking
        if self.last_grid is not None and not getattr(self, 'just_finished_calibration', False):
            M = (self.last_grid != current_grid)
            total_changed = np.sum(M)
            total_pixels = M.shape[0] * M.shape[1]'''

good = '''        # Environment dynamics verification and tracking
        if self.last_grid is not None and not getattr(self, 'just_finished_calibration', False):
            M = (self.last_grid != current_grid)
            if hasattr(self, 'playable_manifold'):
                M_play = M & self.playable_manifold
                total_changed = np.sum(M_play)
            else:
                total_changed = np.sum(M)
            total_pixels = M.shape[0] * M.shape[1]
            
            if getattr(self, 'last_action', None) in [GameAction.ACTION5, GameAction.ACTION6] and total_changed <= 100:
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
                            self.current_path = []'''

if bad in text:
    text = text.replace(bad, good)
    print("SUCCESS: REPLACED TEXT")
else:
    print("ERROR: BAD TEXT NOT FOUND")
    
with open('agent.py', 'w') as f:
    f.write(text)
