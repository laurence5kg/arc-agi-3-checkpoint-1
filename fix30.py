with open('agent.py', 'r') as f:
    text = f.read()

bad = '''                        if best_node == self.agent_pos:
                            self.ignored_targets.add((t_min_y, t_min_x))
                            logger.info(f"Target at {t_min_y, t_min_x} did not react to {self.last_action.name}. Ignoring it.")
                            self.current_path = []'''

good = '''                        logger.info(f"Ignore check for target {t_min_y, t_min_x}: best_node={best_node}, agent_pos={self.agent_pos}")
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
