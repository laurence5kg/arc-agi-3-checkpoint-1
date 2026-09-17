with open('agent.py', 'r') as f:
    text = f.read()

bad = '''    def choose_action(self, frames, latest_frame):
        if not hasattr(self, "_printed_dir"):'''

good = '''    def choose_action(self, frames, latest_frame):
        self.last_agent_pos = getattr(self, 'agent_pos', None)
        self.last_agent_footprint = getattr(self, 'agent_footprint', None)
        if not hasattr(self, "_printed_dir"):'''

if bad in text:
    text = text.replace(bad, good)
    with open('agent.py', 'w') as f:
        f.write(text)
    print("Fixed last_agent_pos at start!")
else:
    print("Could not find block!")
