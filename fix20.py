with open('agent.py', 'r') as f:
    text = f.read()

bad = '''            if getattr(self, 'last_action', None) in [GameAction.ACTION5, GameAction.ACTION6] and total_changed <= 100:'''

good = '''            if getattr(self, 'last_action', None) in [GameAction.ACTION5, GameAction.ACTION6]:
                logger.info(f"Checking ignore logic for {self.last_action.name}. total_changed={total_changed}")
                if total_changed <= 1000:'''

text = text.replace(bad, good)
with open('agent.py', 'w') as f:
    f.write(text)
