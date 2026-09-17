with open('agent.py', 'r') as f:
    text = f.read()

bad = '''        # Calculate manhattan distance to all targets to prioritize
        r_y, r_x = self.agent_pos'''

good = '''        # Calculate manhattan distance to all targets to prioritize
        if self.agent_pos is None:
            logger.error("AGENT POS IS NONE IN get_closest_target_path!")
            return None
        r_y, r_x = self.agent_pos'''

if bad in text:
    text = text.replace(bad, good)
    print("SUCCESS")
else:
    print("FAILED")
with open('agent.py', 'w') as f:
    f.write(text)
