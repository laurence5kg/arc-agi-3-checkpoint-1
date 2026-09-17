with open('agent.py', 'r') as f:
    text = f.read()

bad = '''            if getattr(self, 'last_action', None) in [GameAction.ACTION5, GameAction.ACTION6]:
                logger.info(f"Checking ignore logic for {self.last_action.name}. total_changed={total_changed}")
                if total_changed <= 1000:
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

good = '''            if getattr(self, 'last_action', None) in [GameAction.ACTION5, GameAction.ACTION6]:
                logger.info(f"Checking ignore logic for {self.last_action.name}. total_changed={total_changed}")
                if total_changed <= 1000 and getattr(self, 'agent_pos', None) is not None:
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
    print("SUCCESS")
else:
    print("FAILED")
with open('agent.py', 'w') as f:
    f.write(text)
