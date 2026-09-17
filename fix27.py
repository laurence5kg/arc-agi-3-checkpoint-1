with open('agent.py', 'r') as f:
    text = f.read()

bad = '''            if is_level_transition:
                logger.info(f"LEVEL TRANSITION detected ({total_changed}/{total_pixels} pixels changed)! Replanning...")
                self.current_path = []
                self.environment_changed = True
                self.build_world_model(current_grid, clear_memory=True)
            elif total_changed > 0 and not getattr(self, 'environment_changed', False):
                pass'''

good = '''            if is_level_transition and getattr(self, 'agent_pos', None) is None:
                logger.info(f"LEVEL TRANSITION detected ({total_changed}/{total_pixels} pixels changed) and agent lost! Clearing memory.")
                self.current_path = []
                self.environment_changed = True
                self.build_world_model(current_grid, clear_memory=True)
            elif total_changed > 0 and not getattr(self, 'environment_changed', False):
                pass'''

if bad in text:
    text = text.replace(bad, good)
    print("SUCCESS")
else:
    print("FAILED")
with open('agent.py', 'w') as f:
    f.write(text)
