with open('agent.py', 'r') as f:
    text = f.read()

bad = '''                        for (uy, ux) in getattr(self, 'V', []):
                            dist = abs(uy - t_cy) + abs(ux - t_cx)
                            if dist < best_dist:
                                best_dist = dist
                                best_node = (uy, ux)
                        logger.info(f"Ignore check for target {t_min_y, t_min_x}: best_node={best_node}, agent_pos={self.agent_pos}")
                        if best_node == self.agent_pos:
                            self.ignored_targets.add((t_min_y, t_min_x))
                            logger.info(f"Target at {t_min_y, t_min_x} did not react to {self.last_action.name}. Ignoring it.")
                            self.current_path = []'''

good = '''                        r_y, r_x, h, w, _ = getattr(self, 'agent_footprint', (0, 0, 5, 5, None))
                        is_at_goal = False
                        for (uy, ux) in getattr(self, 'V', []):
                            if abs(uy - t_cy) <= h//2 + 5 and abs(ux - t_cx) <= w//2 + 5:
                                if (uy, ux) == self.agent_pos:
                                    is_at_goal = True
                                    break
                        if is_at_goal:
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
