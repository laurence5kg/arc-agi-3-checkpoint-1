with open('agent.py', 'r') as f:
    text = f.read()

import re
pattern = r"        if getattr\(self, 'agent_pos', None\) is None and hasattr\(self, 'action_mapping'\) and not getattr\(self, 'calibration_phase', False\):.*?                return next_action"
match = re.search(pattern, text, re.DOTALL)
if not match:
    print("Could not find recovery block!")
else:
    good = '''        if getattr(self, 'agent_pos', None) is None and hasattr(self, 'action_mapping') and not getattr(self, 'calibration_phase', False):
            R = None
            if getattr(self, 'last_grid', None) is not None and not np.array_equal(current_grid, self.last_grid):
                kp = self.agent_footprint[4] if hasattr(self, 'agent_footprint') and self.agent_footprint else None
                d, R = self.discover_semantics(self.last_grid, current_grid, known_patch=kp)
            
            if R is not None:
                new_patch = R[4]
                old_patch = self.agent_footprint[4] if hasattr(self, 'agent_footprint') and self.agent_footprint else None
                self.agent_footprint = R
                self.agent_pos = (R[0] + d[0], R[1] + d[1])
                self.initial_agent_footprint = self.agent_footprint
                if old_patch is not None:
                    if not np.array_equal(old_patch, new_patch):
                        logger.warning("Agent footprint changed (color/rotation)! Clearing pruned edges.")
                        self.pruned_edges = set()
                if old_patch is not None and old_patch.shape == new_patch.shape:
                    rot_k = -1
                    for k in range(4):
                        if np.array_equal(np.rot90(old_patch, k=-k), new_patch):
                            rot_k = k
                            break
                    if rot_k != -1 and rot_k != 0:
                        logger.warning(f"Agent rotated by {rot_k * 90} degrees! Updating action mapping.")
                        new_mapping = {}
                        for act, (dy, dx) in self.action_mapping.items():
                            ndy, ndx = dy, dx
                            for _ in range(rot_k):
                                ndy, ndx = ndx, -ndy
                            new_mapping[act] = (ndy, ndx)
                        self.action_mapping = new_mapping
                elif old_patch is not None and old_patch.shape != new_patch.shape:
                    logger.warning("Agent shape changed completely! Re-calibrating.")
                    self.calibration_phase = True
                    self.action_queue = [GameAction.ACTION1, GameAction.ACTION2, GameAction.ACTION3, GameAction.ACTION4]
                    self.action_idx = 0
                    self.action_mapping = {}
                    self.agent_footprint = None
                    self.agent_pos = None
                logger.info(f"Recovered Agent Footprint: {R[2]}x{R[3]} at {self.agent_pos}")
                self.last_grid = current_grid
                if not getattr(self, 'calibration_phase', False):
                    self.build_world_model(current_grid, clear_memory=False)
            else:
                actions = [GameAction.ACTION1, GameAction.ACTION2, GameAction.ACTION3, GameAction.ACTION4]
                idx = actions.index(getattr(self, 'last_action', GameAction.ACTION1)) if getattr(self, 'last_action', None) in actions else -1
                next_action = actions[(idx + 1) % 4]
                logger.info(f"DEBUG: last_action={getattr(self, 'last_action', None)} idx={idx} next={next_action}")
                self.last_grid = current_grid
                self.last_action = next_action
                return next_action
        elif not getattr(self, 'calibration_phase', False):
            # Normal Tracking Loop
            is_normal_move = False
            if hasattr(self, 'agent_pos') and getattr(self, 'agent_pos', None) is not None and getattr(self, 'last_action', None):
                ay, ax = self.agent_pos
                dy, dx = self.action_mapping.get(self.last_action.name, (0, 0))
                expected_y = ay + dy
                expected_x = ax + dx
                self.last_expected_pos = (expected_y, expected_x)
                is_normal_move = self._check_patch_at(current_grid, self.agent_footprint, (expected_y, expected_x))
                if is_normal_move:
                    self.agent_pos = (expected_y, expected_x)
            
            if not is_normal_move:
                if getattr(self, 'agent_pos', None) is not None:
                    ay, ax = self.agent_pos
                    if self._check_patch_at(current_grid, self.agent_footprint, (ay, ax)):
                        # Agent didn't move (hit a wall)
                        self.last_expected_pos = (ay, ax) # update expected to actual since it failed to move
                        if getattr(self, 'last_action', None) is not None:
                            dy, dx = self.action_mapping.get(self.last_action.name, (0, 0))
                            if dy != 0 or dx != 0:
                                expected_pos = (ay + dy, ax + dx)
                                logger.warning(f"Agent collision detected! Expected {expected_pos}, got {self.agent_pos}. Pruned edge.")
                                if not hasattr(self, 'pruned_edges'): self.pruned_edges = set()
                                self.pruned_edges.add(((ay, ax), self.last_action.name))
                                self.current_path = []
                    else:
                        self.agent_pos = None # Lost tracking
            
            if self.agent_pos is None:
                # We lost tracking! We will recover next turn via discover_semantics
                pass'''
    
    text = text[:match.start()] + good + text[match.end():]
    with open('agent.py', 'w') as f:
        f.write(text)
    print("Fixed tracking loop!")
