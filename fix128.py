with open('agent.py', 'r') as f:
    text = f.read()

bad = '''                self.agent_footprint = (found_y, found_x, found_patch.shape[0], found_patch.shape[1], found_patch)
                self.current_path = []
        else:'''

good = '''                self.agent_footprint = (found_y, found_x, found_patch.shape[0], found_patch.shape[1], found_patch)
                
                # Check for collision
                if getattr(self, 'last_agent_pos', None) is not None and getattr(self, 'last_action', None) is not None:
                    d_y, d_x = self.action_mapping.get(self.last_action.name, (0, 0))
                    if d_y != 0 or d_x != 0:
                        p_y, p_x = self.last_agent_pos
                        expected_pos = (p_y + d_y, p_x + d_x)
                        if expected_pos != self.agent_pos:
                            logger.warning(f"Agent collision detected! Expected {expected_pos}, got {self.agent_pos}. Pruned edge.")
                            if not hasattr(self, 'pruned_edges'): self.pruned_edges = set()
                            self.pruned_edges.add(((p_y, p_x), self.last_action.name))
                            self.current_path = []
        else:'''

if bad in text:
    text = text.replace(bad, good)
    with open('agent.py', 'w') as f:
        f.write(text)
    print("Fixed collision pruning and current_path clearing!")
else:
    print("Could not find block!")
