with open('agent.py', 'r', encoding='utf-8') as f:
    text = f.read()

target = '''        if self.calibration_phase:
            if self.action_idx < len(self.action_queue):
                action = self.action_queue[self.action_idx]
                self.action_idx += 1
                return action'''

replacement = '''        if self.calibration_phase:
            if self.last_grid is not None and self.last_action is not None:
                known = self.agent_footprint[4] if self.agent_footprint else None
                d, R = self.discover_semantics(self.last_grid, current_grid, known_patch=known)
                logger.info(f"Calibration: {self.last_action.name} -> displacement {d}")
                if d != (0, 0):
                    self.action_mapping[self.last_action.name] = d
                    if self.agent_footprint is None and R is not None:
                        self.agent_footprint = R
                        self.agent_pos = (R[0], R[1])
                        logger.info(f"Detected Agent Footprint: {R[2]}x{R[3]} at ({R[0]}, {R[1]})")
                    elif hasattr(self, 'agent_pos'):
                        self.agent_pos = (self.agent_pos[0] + d[0], self.agent_pos[1] + d[1])
                else:
                    self.action_mapping[self.last_action.name] = (0, 0)
                    logger.info(f"Calibration: {self.last_action.name} resulted in collision or stationary delta.")

            if self.action_idx < len(self.action_queue):
                action = self.action_queue[self.action_idx]
                self.action_idx += 1
                self.last_action = action
                self.last_grid = current_grid
                return action'''

text = text.replace(target, replacement)

with open('agent.py', 'w', encoding='utf-8') as f:
    f.write(text)
