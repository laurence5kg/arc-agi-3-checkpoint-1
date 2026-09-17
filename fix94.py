with open('agent.py', 'r') as f:
    text = f.read()

bad = '''            if found_y is not None:
                logger.info(f"Re-localized agent from {getattr(self, 'agent_pos', 'Unknown')} to {(found_y, found_x)}")
                self.agent_pos = (found_y, found_x)
                self.agent_footprint = (found_y, found_x, found_patch.shape[0], found_patch.shape[1], found_patch)
                self.current_path = []'''

good = '''            if found_y is not None:
                logger.info(f"Re-localized agent from {getattr(self, 'agent_pos', 'Unknown')} to {(found_y, found_x)}")
                self.agent_pos = (found_y, found_x)
                
                # Check rotation k
                rot_k = -1
                for k in range(4):
                    if np.array_equal(np.rot90(old_patch, k), found_patch):
                        rot_k = k
                        break
                
                if rot_k != -1 and rot_k != 0 and hasattr(self, 'action_mapping'):
                    logger.warning(f"Agent rotated by {rot_k * 90} degrees! Updating action mapping.")
                    new_mapping = {}
                    for act, (dy, dx) in self.action_mapping.items():
                        ndy, ndx = dy, dx
                        for _ in range(rot_k):
                            # np.rot90(patch, 1) is 90 deg counter-clockwise.
                            # So the agent's forward direction rotates 90 deg counter-clockwise.
                            # Math for 90 deg CCW: (x, y) -> (-y, x)? 
                            # Wait! If patch rotates 90 deg CCW, the UP direction (-5, 0) should become LEFT (0, -5).
                            # Let's check: (dy, dx) = (-5, 0).
                            # 90 deg CCW of vector: (dy, dx) -> (-dx, dy).
                            # So (0, -5). This is LEFT! Correct!
                            ndy, ndx = -ndx, ndy
                        new_mapping[act] = (ndy, ndx)
                    self.action_mapping = new_mapping

                self.agent_footprint = (found_y, found_x, found_patch.shape[0], found_patch.shape[1], found_patch)
                self.current_path = []'''

if bad in text:
    text = text.replace(bad, good)
    with open('agent.py', 'w') as f:
        f.write(text)
    print("Patched build_world_model successfully!")
else:
    print("Could not find bad block!")
