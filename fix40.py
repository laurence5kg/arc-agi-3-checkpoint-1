with open('agent.py', 'r') as f:
    text = f.read()

bad = '''        if getattr(self, 'agent_pos', None) is None:
            return getattr(self, 'last_action', GameAction.ACTION1)'''

good = '''        if getattr(self, 'agent_pos', None) is None:
            logger.info("DEBUG: HITTING BOTTOM FALLBACK!")
            return getattr(self, 'last_action', GameAction.ACTION1)'''

if bad in text:
    text = text.replace(bad, good)
    print("SUCCESS")
else:
    print("FAILED")
with open('agent.py', 'w') as f:
    f.write(text)
