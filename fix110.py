with open('agent.py', 'r') as f:
    text = f.read()

bad = '''                p_y, p_x = getattr(self, 'agent_pos', (self.agent_footprint[0], self.agent_footprint[1]))
                dy, dx = self.action_mapping[self.last_action.name]
                expected_pos = (p_y + dy, p_x + dx)'''

good = '''                p_y, p_x = getattr(self, 'agent_pos', (self.agent_footprint[0], self.agent_footprint[1]))
                dy, dx = self.action_mapping[self.last_action.name]
                expected_pos = (p_y + dy, p_x + dx)
                self.last_expected_pos = expected_pos'''

if bad in text:
    text = text.replace(bad, good)
    with open('agent.py', 'w') as f:
        f.write(text)
    print("Fixed last_expected_pos!")
else:
    print("Could not find block!")
