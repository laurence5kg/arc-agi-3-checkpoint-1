with open('agent.py', 'r') as f:
    text = f.read()

bad1 = '''                if curr_lvl not in self.deadly_nodes_by_level:
                    self.deadly_nodes_by_level[curr_lvl] = set()
                self.deadly_nodes_by_level[curr_lvl].add((deadly_y, deadly_x))
                logger.warning(f"Added DEADLY NODE to memory for level {curr_lvl}: {(deadly_y, deadly_x)}")'''

good1 = '''                if not hasattr(self, 'death_delays_by_level'):
                    self.death_delays_by_level = {}
                curr_lvl = getattr(self, 'levels_completed', 0)
                self.death_delays_by_level[curr_lvl] = self.death_delays_by_level.get(curr_lvl, 0) + 1
                logger.warning(f"Incremented death delay for level {curr_lvl} to {self.death_delays_by_level[curr_lvl]}")
                
                # We do NOT mark deadly nodes permanently if it blocks the only path.
                # Instead, we rely on the death delay to shift timing!'''

text = text.replace(bad1, good1)

bad2 = '''                        if getattr(self, 'deadly_nodes_by_level', None):
                            curr_lvl = getattr(self, 'levels_completed', 0)
                            if neighbor in self.deadly_nodes_by_level.get(curr_lvl, set()):
                                continue'''

good2 = '''                        pass # Removed deadly nodes check'''

text = text.replace(bad2, good2)

bad3 = '''        if not hasattr(self, 'current_path') or not self.current_path:
            self.current_path = self.get_closest_target_path()'''

good3 = '''        if not hasattr(self, 'current_path') or not self.current_path:
            curr_lvl = getattr(self, 'levels_completed', 0)
            delay = getattr(self, 'death_delays_by_level', {}).get(curr_lvl, 0)
            
            # If we just reset and have a delay, inject wall-bumping actions to wait!
            if getattr(self, 'just_started_level', False) and delay > 0:
                logger.info(f"Injecting {delay} wait actions to shift timing!")
                # Pick an action that bumps into a wall (or just ACTION5/6 if they do nothing)
                self.current_path = ['ACTION5'] * delay + self.get_closest_target_path()
                self.just_started_level = False
            else:
                self.current_path = self.get_closest_target_path()'''

text = text.replace(bad3, good3)

bad4 = '''        if is_level_transition and getattr(self, 'agent_pos', None) is None:
            logger.info(f"LEVEL TRANSITION detected ({total_changed}/{total_pixels} pixels changed) and agent lost! Clearing memory.")
            self.current_path = []
            self.environment_changed = True
            self.build_world_model(current_grid, clear_memory=True)'''

good4 = '''        if is_level_transition and getattr(self, 'agent_pos', None) is None:
            logger.info(f"LEVEL TRANSITION detected ({total_changed}/{total_pixels} pixels changed) and agent lost! Clearing memory.")
            self.current_path = []
            self.environment_changed = True
            self.just_started_level = True
            self.build_world_model(current_grid, clear_memory=True)'''

text = text.replace(bad4, good4)

with open('agent.py', 'w') as f:
    f.write(text)
print("SUCCESS")
