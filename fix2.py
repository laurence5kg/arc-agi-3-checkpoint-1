import re

with open('agent.py', 'r') as f:
    text = f.read()

bad_block = '''        # Environment dynamics verification and tracking
        if self.last_grid is not None and not getattr(self, 'just_finished_calibration', False):
            M = (self.last_grid != current_grid)
            
            # 1. Update agent position based on expected delta
            if self.last_action and self.last_action.name in self.action_mapping:
                expected_d = self.action_mapping[self.last_action.name]
                if expected_d != (0, 0):
                    expected_y = self.old_agent_pos[0] + expected_d[0]
                    expected_x = self.old_agent_pos[1] + expected_d[1]
                    self.agent_pos = (expected_y, expected_x)
                    
            total_changed = np.sum(M)
            total_pixels = M.shape[0] * M.shape[1]
            
            is_level_transition = (total_changed / total_pixels) > 0.3
            
            if is_level_transition:
                logger.info(f"LEVEL TRANSITION detected ({total_changed}/{total_pixels} pixels changed)! Replanning...")
                self.current_path = []
                self.environment_changed = True
                self.build_world_model(current_grid, clear_memory=True)
            elif total_changed > 0:
                # Dynamic mechanic triggered
                logger.info("Environment dynamics changed! Replanning...")
                self.current_path = []
                self.environment_changed = True
                self.build_world_model(current_grid)
            
        if getattr(self, 'agent_pos', None) is not None:
            patch = self.agent_footprint
            p_y, p_x = self.agent_pos
            if not self._check_patch_at(current_grid, patch, (p_y, p_x)):
                # Agent is not where it was. Either it moved, or level transitioned.
                d_y, d_x = 0, 0
                if getattr(self, 'last_action', None) and hasattr(self, 'action_mapping'):
                    d_y, d_x = self.action_mapping.get(self.last_action.name, (0, 0))
                
                expected_pos = (self.agent_pos[0] + d_y, self.agent_pos[1] + d_x)
                if not self._check_patch_at(current_grid, patch, expected_pos):
                    # Check if it didn't move because it hit a wall
                    if self._check_patch_at(current_grid, patch, self.agent_pos):
                        self.pruned_edges.add((self.agent_pos, self.last_action.name))
                        logger.warning(f"Agent collision detected! Pruned edge {self.last_action.name} from {self.agent_pos}")
                        self.environment_changed = True
                        self.build_world_model(current_grid)
                    else:
                        found = False
                        # Search entire grid for patch
                        ph, pw, h, w, p_color = patch
                        best_y, best_x = -1, -1
                        for ry in range(0, h - ph + 1):
                            for rx in range(0, w - pw + 1):
                                if self._check_patch_at(current_grid, patch, (ry, rx)):
                                    best_y, best_x = ry, rx
                                    found = True
                                    break
                            if found:
                                break
                                
                        if found:
                            self.agent_pos = (best_y, best_x)
                            self.current_path = []
                            self.environment_changed = True
                            logger.info(f"Re-localized agent from {(p_y, p_x)} to {(best_y, best_x)}")
                            self.build_world_model(current_grid)
                        else:
                            logger.warning("Re-localization FAILED on level transition! Forcing agent re-extraction via movement.")
                            self.agent_pos = None
                            # clear path so it doesn't continue blindly
                            self.current_path = []
                else:
                    self.agent_pos = expected_pos'''

start_idx = text.find('        # Environment dynamics verification and tracking')
end_idx = text.find('        if getattr(self, \'agent_pos\', None) is None:')

bad_block = text[start_idx:end_idx]

good_block = '''        # Environment dynamics verification and tracking
        if self.last_grid is not None and not getattr(self, 'just_finished_calibration', False):
            M = (self.last_grid != current_grid)
            total_changed = np.sum(M)
            total_pixels = M.shape[0] * M.shape[1]
            
            is_level_transition = (total_changed / total_pixels) > 0.3
            
            if getattr(self, 'agent_pos', None) is not None:
                patch = self.agent_footprint
                p_y, p_x = self.agent_pos
                
                # Check where we actually ended up
                d_y, d_x = 0, 0
                if getattr(self, 'last_action', None) and hasattr(self, 'action_mapping'):
                    d_y, d_x = self.action_mapping.get(self.last_action.name, (0, 0))
                    
                expected_pos = (p_y + d_y, p_x + d_x)
                
                if d_y != 0 or d_x != 0:
                    if self._check_patch_at(current_grid, patch, expected_pos):
                        self.agent_pos = expected_pos
                    else:
                        if self._check_patch_at(current_grid, patch, (p_y, p_x)):
                            logger.warning(f"Agent collision detected! Pruned edge {self.last_action.name} from {self.agent_pos}")
                            self.pruned_edges.add((self.agent_pos, self.last_action.name))
                            self.environment_changed = True
                            self.build_world_model(current_grid)
                        else:
                            found = False
                            ph, pw, h, w, p_color = patch
                            best_y, best_x = -1, -1
                            for ry in range(0, h - ph + 1):
                                for rx in range(0, w - pw + 1):
                                    if self._check_patch_at(current_grid, patch, (ry, rx)):
                                        best_y, best_x = ry, rx
                                        found = True
                                        break
                                if found:
                                    break
                            
                            if found:
                                self.agent_pos = (best_y, best_x)
                                self.current_path = []
                                self.environment_changed = True
                                logger.info(f"Re-localized agent from {(p_y, p_x)} to {self.agent_pos}")
                                self.build_world_model(current_grid, clear_memory=is_level_transition)
                            else:
                                logger.warning("Re-localization FAILED on level transition! Forcing agent re-extraction via movement.")
                                self.agent_pos = None
                                self.current_path = []
                else:
                    if not self._check_patch_at(current_grid, patch, (p_y, p_x)):
                        found = False
                        ph, pw, h, w, p_color = patch
                        best_y, best_x = -1, -1
                        for ry in range(0, h - ph + 1):
                            for rx in range(0, w - pw + 1):
                                if self._check_patch_at(current_grid, patch, (ry, rx)):
                                    best_y, best_x = ry, rx
                                    found = True
                                    break
                                if found:
                                    break
                        if found:
                            self.agent_pos = (best_y, best_x)
                            self.current_path = []
                            self.environment_changed = True
                            self.build_world_model(current_grid, clear_memory=is_level_transition)
                        else:
                            self.agent_pos = None
                            self.current_path = []

            if is_level_transition:
                logger.info(f"LEVEL TRANSITION detected ({total_changed}/{total_pixels} pixels changed)! Replanning...")
                self.current_path = []
                self.environment_changed = True
                if getattr(self, 'agent_pos', None) is not None:
                    self.build_world_model(current_grid, clear_memory=True)
            elif total_changed > 0 and not getattr(self, 'environment_changed', False):
                # If only environment changed, not handled by collision or re-localization
                # wait, if agent moved, M > 0.
                pass # Only replan on level transition or collision/re-localization

'''

text = text.replace(bad_block, good_block)

with open('agent.py', 'w') as f:
    f.write(text)

