with open('agent.py', 'r') as f:
    text = f.read()

bad = '''        if getattr(self, 'agent_pos', None) is None and hasattr(self, 'action_mapping') and not getattr(self, 'calibration_phase', False):
            if getattr(self, 'last_grid', None) is not None and not np.array_equal(current_grid, self.last_grid):
                d, R = self.discover_semantics(self.last_grid, current_grid, known_patch=None)
                if R is not None:
                    self.agent_footprint = R
                    self.agent_pos = (R[0] + d[0], R[1] + d[1])
                    self.initial_agent_footprint = self.agent_footprint
                    logger.info(f"Recovered Agent Footprint: {R[2]}x{R[3]} at {self.agent_pos}")
                    self.last_grid = current_grid
                    self.build_world_model(current_grid, clear_memory=False)
                else:
                    # Fall through to cycle actions
                    pass
            else:
                actions = [GameAction.ACTION1, GameAction.ACTION2, GameAction.ACTION3, GameAction.ACTION4]
                idx = actions.index(getattr(self, 'last_action', GameAction.ACTION1)) if getattr(self, 'last_action', None) in actions else -1
                next_action = actions[(idx + 1) % 4]
                self.last_grid = current_grid
                self.last_action = next_action
                return next_action'''

good = '''        if getattr(self, 'agent_pos', None) is None and hasattr(self, 'action_mapping') and not getattr(self, 'calibration_phase', False):
            R = None
            if getattr(self, 'last_grid', None) is not None and not np.array_equal(current_grid, self.last_grid):
                d, R = self.discover_semantics(self.last_grid, current_grid, known_patch=None)
            
            if R is not None:
                self.agent_footprint = R
                self.agent_pos = (R[0] + d[0], R[1] + d[1])
                self.initial_agent_footprint = self.agent_footprint
                logger.info(f"Recovered Agent Footprint: {R[2]}x{R[3]} at {self.agent_pos}")
                self.last_grid = current_grid
                self.build_world_model(current_grid, clear_memory=False)
            else:
                actions = [GameAction.ACTION1, GameAction.ACTION2, GameAction.ACTION3, GameAction.ACTION4]
                idx = actions.index(getattr(self, 'last_action', GameAction.ACTION1)) if getattr(self, 'last_action', None) in actions else -1
                next_action = actions[(idx + 1) % 4]
                self.last_grid = current_grid
                self.last_action = next_action
                return next_action'''

if bad in text:
    text = text.replace(bad, good)
    print("SUCCESS")
else:
    print("FAILED")
with open('agent.py', 'w') as f:
    f.write(text)
