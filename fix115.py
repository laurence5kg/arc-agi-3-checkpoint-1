with open('agent.py', 'r') as f:
    text = f.read()

bad = '''    def choose_action(self, frames, latest_frame):
        if latest_frame.state == GameState.GAMEOVER:'''

good = '''    def choose_action(self, frames, latest_frame):
        self.last_agent_pos = getattr(self, 'agent_pos', None)
        self.last_agent_footprint = getattr(self, 'agent_footprint', None)
        if latest_frame.state == GameState.GAMEOVER:'''

if bad in text:
    text = text.replace(bad, good)
    with open('agent.py', 'w') as f:
        f.write(text)
    print("Fixed last_agent_pos at start!")
else:
    print("Could not find block!")
