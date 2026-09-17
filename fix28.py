with open('agent.py', 'r') as f:
    text = f.read()

bad = '''                                logger.info(f"Re-localized agent from {(p_y, p_x)} to {self.agent_pos}")
                                self.build_world_model(current_grid, clear_memory=is_level_transition)'''

good = '''                                logger.info(f"Re-localized agent from {(p_y, p_x)} to {self.agent_pos}")
                                self.build_world_model(current_grid, clear_memory=False)'''

if bad in text:
    text = text.replace(bad, good)
    print("SUCCESS")
else:
    print("FAILED")
with open('agent.py', 'w') as f:
    f.write(text)
