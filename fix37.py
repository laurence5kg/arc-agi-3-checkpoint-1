with open('agent.py', 'r') as f:
    text = f.read()

bad = '''                if R is not None:
                    self.agent_footprint = R
                    self.agent_pos = (R[0] + d[0], R[1] + d[1])
                    self.initial_agent_footprint = self.agent_footprint
                    logger.info(f"Recovered Agent Footprint: {R[2]}x{R[3]} at {self.agent_pos}")
                    self.last_grid = current_grid
                    self.build_world_model(current_grid, clear_memory=False)
                else:
                    # If R is None despite grid changing, maybe we moved into a target? 
                    # Try next action anyway
                    self.last_grid = current_grid
                    return GameAction.ACTION1'''

good = '''                if R is not None:
                    self.agent_footprint = R
                    self.agent_pos = (R[0] + d[0], R[1] + d[1])
                    self.initial_agent_footprint = self.agent_footprint
                    logger.info(f"Recovered Agent Footprint: {R[2]}x{R[3]} at {self.agent_pos}")
                    self.last_grid = current_grid
                    self.build_world_model(current_grid, clear_memory=False)
                else:
                    # Fall through to cycle actions
                    pass'''

if bad in text:
    text = text.replace(bad, good)
    print("SUCCESS")
else:
    print("FAILED")
with open('agent.py', 'w') as f:
    f.write(text)
