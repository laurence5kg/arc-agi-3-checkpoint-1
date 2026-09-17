with open('agent.py', 'r') as f:
    text = f.read()

bad = '''            else:
                actions = [GameAction.ACTION1, GameAction.ACTION2, GameAction.ACTION3, GameAction.ACTION4]
                idx = actions.index(getattr(self, 'last_action', GameAction.ACTION1)) if getattr(self, 'last_action', None) in actions else -1
                next_action = actions[(idx + 1) % 4]
                self.last_grid = current_grid
                self.last_action = next_action
                return next_action'''

good = '''            else:
                actions = [GameAction.ACTION1, GameAction.ACTION2, GameAction.ACTION3, GameAction.ACTION4]
                idx = actions.index(getattr(self, 'last_action', GameAction.ACTION1)) if getattr(self, 'last_action', None) in actions else -1
                next_action = actions[(idx + 1) % 4]
                logger.info(f"DEBUG: last_action={getattr(self, 'last_action', None)} idx={idx} next={next_action}")
                self.last_grid = current_grid
                self.last_action = next_action
                return next_action'''

if bad in text:
    text = text.replace(bad, good)
    print("SUCCESS")
else:
    print("FAILED")
with open('agent.py', 'w') as f:
    f.write(text)
