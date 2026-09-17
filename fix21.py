with open('agent.py', 'r') as f:
    text = f.read()

bad = '''            if getattr(self, 'last_action', None) in [GameAction.ACTION5, GameAction.ACTION6]:
                logger.info(f"Checking ignore logic for {self.last_action.name}. total_changed={total_changed}")
                if total_changed <= 1000:
                if getattr(self, 'agent_pos', None) is not None:'''

good = '''            if getattr(self, 'last_action', None) in [GameAction.ACTION5, GameAction.ACTION6]:
                logger.info(f"Checking ignore logic for {self.last_action.name}. total_changed={total_changed}")
                if total_changed <= 1000:
                    if getattr(self, 'agent_pos', None) is not None:'''

if bad in text:
    text = text.replace(bad, good)
    print("SUCCESS")
else:
    print("FAILED")
with open('agent.py', 'w') as f:
    f.write(text)
