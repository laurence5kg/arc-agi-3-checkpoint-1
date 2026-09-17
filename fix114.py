with open('agent.py', 'r') as f:
    text = f.read()

bad = '''            if getattr(self, 'agent_pos', None) is not None:
                patch = self.agent_footprint
                p_y, p_x = self.agent_pos'''

good = '''            if getattr(self, 'agent_pos', None) is not None:
                patch = getattr(self, 'last_agent_footprint', self.agent_footprint)
                p_y, p_x = getattr(self, 'last_agent_pos', self.agent_pos)
                if p_y is None: p_y, p_x = self.agent_pos'''

if bad in text:
    text = text.replace(bad, good)
    with open('agent.py', 'w') as f:
        f.write(text)
    print("Fixed p_y, p_x!")
else:
    print("Could not find block!")
