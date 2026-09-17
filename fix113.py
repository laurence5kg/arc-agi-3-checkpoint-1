with open('agent.py', 'r') as f:
    text = f.read()

bad = '''                p_y, p_x = getattr(self, 'agent_pos', (self.agent_footprint[0], self.agent_footprint[1]))
                if getattr(self, 'last_action', None) and hasattr(self, 'action_mapping'):'''

good = '''                p_y, p_x = getattr(self, 'last_agent_pos', getattr(self, 'agent_pos', (self.agent_footprint[0], self.agent_footprint[1])))
                if p_y is None: p_y = getattr(self, 'agent_pos', (0,0))[0]
                if p_x is None: p_x = getattr(self, 'agent_pos', (0,0))[1]
                if getattr(self, 'last_action', None) and hasattr(self, 'action_mapping'):'''

if bad in text:
    text = text.replace(bad, good)
    with open('agent.py', 'w') as f:
        f.write(text)
    print("Fixed p_y, p_x in build_world_model!")
else:
    print("Could not find block!")
