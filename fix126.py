with open('agent.py', 'r') as f:
    text = f.read()

bad = '''            if not is_level_transition and getattr(self, 'agent_pos', None) is not None:'''

good = '''            if not is_level_transition and getattr(self, 'agent_pos', None) is not None and getattr(self, 'last_agent_pos', None) is not None:'''

if bad in text:
    text = text.replace(bad, good)
    with open('agent.py', 'w') as f:
        f.write(text)
    print("Fixed ignore logic for mechanic!")
else:
    print("Could not find block!")
