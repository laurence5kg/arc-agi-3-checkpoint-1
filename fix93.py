with open('agent.py', 'r') as f:
    text = f.read()

bad = '''            if R is not None:
                self.agent_footprint = R
                self.agent_pos = (R[0] + d[0], R[1] + d[1])
                self.initial_agent_footprint = self.agent_footprint'''

good = '''            if R is not None:
                new_patch = R[4]
                old_patch = self.agent_footprint[4] if hasattr(self, 'agent_footprint') and self.agent_footprint else None
                self.agent_footprint = R
                self.agent_pos = (R[0] + d[0], R[1] + d[1])
                self.initial_agent_footprint = self.agent_footprint
                if old_patch is not None and old_patch.shape == new_patch.shape:
                    import numpy as np
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
                    self.agent_pos = None'''

if bad in text:
    text = text.replace(bad, good)
    with open('agent.py', 'w') as f:
        f.write(text)
    print("Patched agent.py successfully!")
else:
    print("Could not find bad block!")
