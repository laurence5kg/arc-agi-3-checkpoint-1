with open('agent.py', 'r') as f:
    text = f.read()

bad = '''            # Check if we took an interaction action and nothing happened
            if getattr(self, 'last_action', None) in [GameAction.ACTION5, GameAction.ACTION6] and total_changed <= 10:'''

good = '''            # Check if we took an interaction action and nothing happened
            if getattr(self, 'last_action', None) in [GameAction.ACTION5, GameAction.ACTION6]:
                logger.info(f"Tracking Action5/6: total_changed={total_changed}")
                if total_changed <= 100:'''

text = text.replace(bad, good)
with open('agent.py', 'w') as f:
    f.write(text)
